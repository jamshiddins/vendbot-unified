import json
from typing import List, Dict
from pathlib import Path
from decimal import Decimal
import logging

from ..models.audit_models import Recipe, RecipeIngredient
from .base_loader import BaseLoader

logger = logging.getLogger(__name__)

class RecipeLoader(BaseLoader):
    """Загрузчик рецептов"""
    
    def load(self) -> Dict[str, Recipe]:
        """Загрузка рецептов из JSON файла"""
        logger.info(f"Loading recipes from {self.filepath}")
        
        try:
            with open(self.filepath, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            recipes = {}
            for recipe_data in data.get('recipes', []):
                recipe = self._parse_recipe(recipe_data)
                recipes[recipe.product_code] = recipe
            
            logger.info(f"Loaded {len(recipes)} recipes")
            return recipes
            
        except Exception as e:
            logger.error(f"Error loading recipes: {e}")
            raise
    
    def _parse_recipe(self, data: dict) -> Recipe:
        """Парсинг рецепта"""
        ingredients = []
        
        for ing_data in data.get('ingredients', []):
            ingredient = RecipeIngredient(
                ingredient_code=ing_data['code'],
                ingredient_name=ing_data['name'],
                quantity=Decimal(str(ing_data['quantity'])),
                unit=ing_data.get('unit', 'g')
            )
            ingredients.append(ingredient)
        
        return Recipe(
            product_code=data['product_code'],
            product_name=data['product_name'],
            ingredients=ingredients,
            category=data.get('category', 'coffee')
        )