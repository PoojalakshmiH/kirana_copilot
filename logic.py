def recommend_quantity(stock, target_stock):
    return max(0, int(target_stock) - int(stock))

def create_recommendations(inventory, budget):
    """Budget-aware simple recommendation; inventory is a list of dicts."""
    candidates = sorted(
        (row for row in inventory if row['stock'] < row['min_stock'] and row['expiry_days'] > 7),
        key=lambda row: row['daily_sales'] / (row['stock'] + 1),
        reverse=True,
    )
    recommendations=[]
    remaining=float(budget)
    for row in candidates:
        qty=recommend_quantity(row['stock'],row['target_stock'])
        qty=min(qty,int(remaining//row['unit_price']))
        if qty>0:
            cost=qty*row['unit_price']
            recommendations.append({'product':row['product'],'quantity':qty,'unit_price':row['unit_price'],'cost':cost})
            remaining-=cost
    return recommendations
