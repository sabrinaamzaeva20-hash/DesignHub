from decimal import Decimal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
app = FastAPI(title="DesignHub Pricing Service")
PRICES = {"Брендинг":Decimal("65"),"Соцсети":Decimal("8"),"Веб-дизайн":Decimal("90"),"Полиграфия":Decimal("18")}
class EstimateInput(BaseModel):
    category: str
    quantity: int = Field(ge=1,le=1000)
    urgency: bool = False
@app.get("/health")
def health():
    return {"ok":True}
@app.post("/calculate")
def calculate(item: EstimateInput):
    if item.category not in PRICES:
        raise HTTPException(status_code=422,detail="Неизвестная категория")
    price=PRICES[item.category]
    total=price*item.quantity*(Decimal("1.25") if item.urgency else Decimal("1"))
    return {"category":item.category,"quantity":item.quantity,"price_per_item_usd":float(price),"urgency":item.urgency,"total_usd":float(total),"currency":"USD"}
