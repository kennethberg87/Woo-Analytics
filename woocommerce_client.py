```python
# In process_orders_to_df method, where we handle line items and costs:
                    # Process line items
                    for item in order.get('line_items', []):
                        quantity = int(item.get('quantity', 0))
                        cost = 0
                        for meta in item.get('meta_data', []):
                            if meta.get('key') == '_yith_cog_item_cost':
                                try:
                                    cost = float(meta.get('value', 0))
                                except (ValueError, TypeError):
                                    cost = 0
                                break

                        # Get stock quantity from cached data
                        product_id = item.get('product_id')
                        stock_quantity = stock_quantities.get(product_id)

                        product_data.append({
                            'date': order_date,
                            'product_id': product_id,
                            'sku': item.get('sku', ''),  # Add SKU field
                            'name': item.get('name'),
                            'quantity': quantity,
                            'total': float(item.get('total', 0)) + float(item.get('total_tax', 0)),
                            'subtotal': float(item.get('subtotal', 0)),
                            'tax': float(item.get('total_tax', 0)),
                            'cost': cost * quantity,  # Total cost for this line item
                            'stock_quantity': stock_quantity
                        })
```
