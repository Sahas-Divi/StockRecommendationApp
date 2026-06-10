from pydantic import BaseModel, Field
from typing import Literal

class StockNews(BaseModel):
    ticker_symbol: str = Field(description="The ticker symbol given by the user")
    comapny: str = Field(description="The company that the ticker symbol represents")
    news: str = Field(description="All stock news and headlines important to any investor")

class StockRecommendation(BaseModel):
    recommendation: Literal["buy", "short"]
    reason: str = Field(description="A detailed reason for the recommendation made")


