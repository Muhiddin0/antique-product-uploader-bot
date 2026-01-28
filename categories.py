"""Category and Brand selection agent using OpenAI."""

import difflib
import json
import logging
import os
import re
from typing import Any, Dict, List, Optional

from pydantic import ValidationError, BaseModel, Field

# OpenAI API uchun
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Global OpenAI client (lazy initialization)
_client = None


def _get_openai_client():
    """Get or create OpenAI client."""
    global _client
    if _client is None:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not OPENAI_AVAILABLE or not openai_api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        _client = openai.OpenAI(api_key=openai_api_key)
    return _client


class CategoryBrandSelectionSchema(BaseModel):
    """Schema for category and brand selection by AI."""

    category_id: str = Field(..., description="Selected category ID")
    category: Optional[str] = Field(None, description="Selected category name")
    sub_category_id: Optional[str] = Field(None, description="Selected sub-category ID")
    sub_category: Optional[str] = Field(None, description="Selected sub-category name")
    sub_sub_category_id: Optional[str] = Field(
        None, description="Selected sub-sub-category ID"
    )
    sub_sub_category: Optional[str] = Field(
        None, description="Selected sub-sub-category name"
    )
    sub_sub_sub_category_id: Optional[str] = Field(
        None, description="Selected sub-sub-sub-category ID"
    )
    sub_sub_sub_category: Optional[str] = Field(
        None, description="Selected sub-sub-sub-category name"
    )
    brand_id: int = Field(..., description="Selected brand ID")




def _build_categories_tree(
    categories: List[Dict[str, Any]],
    parent_id: Optional[str] = None,
    level: str = "category",
) -> List[Dict[str, Any]]:
    """Build a simplified structure for categories at a specific level."""
    result = []

    if level == "category":
        for cat in categories:
            result.append({"id": str(cat["id"]), "name": cat["name"]})
    elif level == "sub_category" and parent_id:
        for cat in categories:
            if str(cat["id"]) == parent_id:
                for sub_cat in cat.get("childes", []):
                    result.append({"id": str(sub_cat["id"]), "name": sub_cat["name"]})
                break
    elif level == "sub_sub_category" and parent_id:
        # parent_id here is the sub_category_id, so we need to find it across all main categories
        for cat in categories:
            for sub_cat in cat.get("childes", []):
                if str(sub_cat["id"]) == parent_id:
                    for sub_sub_cat in sub_cat.get("childes", []):
                        result.append(
                            {"id": str(sub_sub_cat["id"]), "name": sub_sub_cat["name"]}
                        )
                    return result
    elif level == "sub_sub_sub_category" and parent_id:
        # parent_id here is the sub_sub_category_id
        for cat in categories:
            for sub_cat in cat.get("childes", []):
                for sub_sub_cat in sub_cat.get("childes", []):
                    if str(sub_sub_cat["id"]) == parent_id:
                        for sub_sub_sub_cat in sub_sub_cat.get("childes", []):
                            result.append(
                                {"id": str(sub_sub_sub_cat["id"]), "name": sub_sub_sub_cat["name"]}
                            )
                        return result
    return result





def _select_step(
    prompt_level: str,
    product_name: str,
    brand_name: str,
    options: List[Dict[str, Any]],
    model: str,
    temperature: float,
) -> Optional[Dict[str, Any]]:
    """Helper to perform a single AI selection step."""
    if not options:
        return None

    system_prompt = f"""
You are a category selection assistant.
Select the most appropriate {prompt_level.replace('_', ' ')} ID based on the product name and brand.

Return ONLY valid JSON:
{{
  "id": "string",
  "name": "string"
}}
""".strip()

    user_prompt = f"""
Product: {product_name}
Brand: {brand_name}

Available {prompt_level.replace('_', ' ')}s:
{json.dumps(options, ensure_ascii=False)}

Select the ID. Return ONLY JSON.
""".strip()

    try:
        client = _get_openai_client()
        resp = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        content = (resp.choices[0].message.content or "").strip()
        # Remove markdown code blocks if present
        content = re.sub(r'```json\s*', '', content, flags=re.IGNORECASE)
        content = re.sub(r'```\s*$', '', content).strip()
        return json.loads(content)
    except Exception as e:
        logging.warning(f"AI selection step failed: {str(e)}")
        return None





def _match_brand_by_name(brand_name: str, brands: List[Dict[str, Any]]) -> int:
    """Match brand by name using fuzzy matching."""
    if not brand_name or not brands:
        return brands[0].get("id", 0) if brands else 0
    
    brand_name_lower = brand_name.lower().strip()
    
    # Exact match
    for brand in brands:
        if brand.get("name", "").lower() == brand_name_lower:
            return brand.get("id", 0)
    
    # Partial match
    for brand in brands:
        brand_name_db = brand.get("name", "").lower()
        if brand_name_lower in brand_name_db or brand_name_db in brand_name_lower:
            return brand.get("id", 0)
    
    # Fuzzy match using difflib
    brand_names = [b.get("name", "").lower() for b in brands]
    matches = difflib.get_close_matches(brand_name_lower, brand_names, n=1, cutoff=0.6)
    if matches:
        matched_name = matches[0]
        for brand in brands:
            if brand.get("name", "").lower() == matched_name:
                return brand.get("id", 0)
    
    # Default: return first brand
    return brands[0].get("id", 0) if brands else 0


def select_category_brand(
    product_name: str,
    brand_name: str,
    categories: List[Dict[str, Any]],
    brands: List[Dict[str, Any]],
    model: Optional[str] = None,
    temperature: Optional[float] = None,
) -> CategoryBrandSelectionSchema:
    """
    Select category and brand IDs using AI based on product name and brand.
    Uses 3-step process (Category -> Sub-category -> Sub-sub-category) to reduce tokens.
    
    Args:
        product_name: Product name
        brand_name: Brand name (can be extracted from product name/description)
        categories: List of category dictionaries
        brands: List of brand dictionaries
        model: OpenAI model name (default: "gpt-4o-mini")
        temperature: Temperature for AI (default: 0.3)
    
    Returns:
        CategoryBrandSelectionSchema with selected IDs
    """
    # Set defaults
    if model is None:
        model = "gpt-4o-mini"
    if temperature is None:
        temperature = 0.3

    # 1. Match brand using Python logic (Fast, no AI)
    brand_id = _match_brand_by_name(brand_name, brands)

    # 2. Step-by-step category selection
    result = {
        "category_id": "0",
        "category": None,
        "sub_category_id": None,
        "sub_category": None,
        "sub_sub_category_id": None,
        "sub_sub_category": None,
        "brand_id": brand_id,
    }

    # Step A: Main Category
    main_options = _build_categories_tree(categories, level="category")
    main_sel = _select_step(
        "category", product_name, brand_name, main_options, model, temperature
    )

    if main_sel and "id" in main_sel:
        result["category_id"] = main_sel["id"]
        result["category"] = main_sel.get("name")

        # Step B: Sub Category
        sub_options = _build_categories_tree(
            categories, parent_id=main_sel["id"], level="sub_category"
        )
        if sub_options:
            sub_sel = _select_step(
                "sub_category",
                product_name,
                brand_name,
                sub_options,
                model,
                temperature,
            )
            if sub_sel and "id" in sub_sel:
                result["sub_category_id"] = sub_sel["id"]
                result["sub_category"] = sub_sel.get("name")

                # Step C: Sub-sub Category
                sub_sub_options = _build_categories_tree(
                    categories, parent_id=sub_sel["id"], level="sub_sub_category"
                )
                if sub_sub_options:
                    ss_sel = _select_step(
                        "sub_sub_category",
                        product_name,
                        brand_name,
                        sub_sub_options,
                        model,
                        temperature,
                    )
                    if ss_sel and "id" in ss_sel:
                        result["sub_sub_category_id"] = ss_sel["id"]
                        result["sub_sub_category"] = ss_sel.get("name")

                        # Step D: Sub-sub-sub Category
                        sub_sub_sub_options = _build_categories_tree(
                            categories, parent_id=ss_sel["id"], level="sub_sub_sub_category"
                        )
                        if sub_sub_sub_options:
                            sss_sel = _select_step(
                                "sub_sub_sub_category",
                                product_name,
                                brand_name,
                                sub_sub_sub_options,
                                model,
                                temperature,
                            )
                            if sss_sel and "id" in sss_sel:
                                result["sub_sub_sub_category_id"] = sss_sel["id"]
                                result["sub_sub_sub_category"] = sss_sel.get("name")

    try:
        selection = CategoryBrandSelectionSchema(**result)
        return selection
    except ValidationError as e:
        # Return a fallback schema if validation fails after AI steps
        return CategoryBrandSelectionSchema(
            category_id=result["category_id"] or "0",
            category=result.get("category"),
            brand_id=brand_id,
        )
