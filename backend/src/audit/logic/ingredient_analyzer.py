from typing import List, Dict, Optional
from datetime import datetime
from decimal import Decimal
from collections import defaultdict
import logging

from ..models.audit_models import (
    SaleRecord, Recipe, InventoryMovement,
    Discrepancy, DiscrepancyType
)

logger = logging.getLogger(__name__)

class IngredientAnalyzer:
    """Анализатор расхода ингредиентов"""
    
    def __init__(self, tolerance_percent: float = 5.0):
        self.tolerance_percent = tolerance_percent
    
    def analyze_consumption(self,
                           sales: List[SaleRecord],
                           recipes: Dict[str, Recipe],
                           inventory_movements: List[InventoryMovement],
                           machine_id: str,
                           period_start: datetime,
                           period_end: datetime) -> List[Discrepancy]:
        """Анализ расхода ингредиентов"""
        logger.info(f"Analyzing ingredient consumption for machine {machine_id}")
        
        # 1. Рассчитываем теоретический расход на основе продаж
        theoretical = self._calculate_theoretical_consumption(sales, recipes, machine_id)
        
        # 2. Получаем фактическое пополнение
        actual_refills = self._get_actual_refills(inventory_movements, machine_id, 
                                                  period_start, period_end)
        
        # 3. Сравниваем и находим отклонения
        discrepancies = self._compare_consumption(theoretical, actual_refills, machine_id)
        
        return discrepancies
    
    def _calculate_theoretical_consumption(self,
                                         sales: List[SaleRecord],
                                         recipes: Dict[str, Recipe],
                                         machine_id: str) -> Dict[str, Decimal]:
        """Расчет теоретического расхода ингредиентов"""
        consumption = defaultdict(Decimal)
        
        machine_sales = [s for s in sales if s.machine_id == machine_id]
        
        for sale in machine_sales:
            recipe = recipes.get(sale.product_code)
            if not recipe:
                logger.warning(f"Recipe not found for product: {sale.product_code}")
                continue
            
            # Умножаем количество каждого ингредиента на количество проданных напитков
            for ingredient in recipe.ingredients:
                consumption[ingredient.ingredient_code] += ingredient.quantity * sale.quantity
        
        return dict(consumption)
    
    def _get_actual_refills(self,
                           movements: List[InventoryMovement],
                           machine_id: str,
                           period_start: datetime,
                           period_end: datetime) -> Dict[str, Decimal]:
        """Получение фактических пополнений"""
        refills = defaultdict(Decimal)
        
        for movement in movements:
            if (movement.machine_id == machine_id and
                movement.movement_type == 'refill' and
                period_start <= movement.datetime <= period_end):
                refills[movement.ingredient_code] += movement.quantity
        
        return dict(refills)
    
    def _compare_consumption(self,
                           theoretical: Dict[str, Decimal],
                           actual_refills: Dict[str, Decimal],
                           machine_id: str) -> List[Discrepancy]:
        """Сравнение теоретического и фактического расхода"""
        discrepancies = []
        
        # Проверяем каждый ингредиент
        all_ingredients = set(theoretical.keys()) | set(actual_refills.keys())
        
        for ingredient_code in all_ingredients:
            theo_amount = theoretical.get(ingredient_code, Decimal('0'))
            actual_amount = actual_refills.get(ingredient_code, Decimal('0'))
            
            if theo_amount == 0:
                # Пополнение без продаж
                if actual_amount > 0:
                    discrepancies.append(Discrepancy(
                        type=DiscrepancyType.EXCESS_CONSUMPTION,
                        machine_id=machine_id,
                        datetime=datetime.now(),
                        description=f"Refill without sales for {ingredient_code}: {actual_amount}",
                        severity="medium"
                    ))
            else:
                # Рассчитываем процент отклонения
                variance_percent = ((actual_amount - theo_amount) / theo_amount) * 100
                
                if abs(variance_percent) > self.tolerance_percent:
                    severity = self._get_severity(variance_percent)
                    
                    discrepancies.append(Discrepancy(
                        type=DiscrepancyType.EXCESS_CONSUMPTION,
                        machine_id=machine_id,
                        datetime=datetime.now(),
                        description=(f"Consumption variance for {ingredient_code}: "
                                   f"theoretical={theo_amount}, actual={actual_amount}, "
                                   f"variance={variance_percent:.1f}%"),
                        amount_difference=actual_amount - theo_amount,
                        severity=severity
                    ))
        
        return discrepancies
    
    def _get_severity(self, variance_percent: float) -> str:
        """Определение серьезности отклонения"""
        abs_variance = abs(variance_percent)
        
        if abs_variance > 20:
            return "critical"
        elif abs_variance > 10:
            return "high"
        elif abs_variance > 5:
            return "medium"
        else:
            return "low"