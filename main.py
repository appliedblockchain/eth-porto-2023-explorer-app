from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from explorer import Explorer

app = FastAPI()

templates = Jinja2Templates(directory="views")

explorer = Explorer()

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
  return templates.TemplateResponse("index.jinja", {"request": request})

@app.get("/erc20s", response_class=HTMLResponse)
async def erc20(request: Request):
  return templates.TemplateResponse("erc20s.jinja", {"request": request})

@app.get("/transactions/nft", response_class=HTMLResponse)
async def transactions_nft(request: Request, block_num: int):
  transactions = explorer.get_transactions_nft(block_num)
  return templates.TemplateResponse("transactions_nft.jinja", {"block_num": block_num, "transactions": transactions, "request": request})

@app.get("/transactions/erc20", response_class=HTMLResponse)
async def transactions_erc20(request: Request, block_num: int):
  transactions = explorer.get_transactions_erc20(block_num)
  return templates.TemplateResponse("transactions_erc20.jinja", {"block_num": block_num, "transactions": transactions, "request": request})
