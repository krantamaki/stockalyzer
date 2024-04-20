"""
File containing the table specifications for the used database

Note since many modules depend on the information here DO NOT change it
"""

"""
Dictionary specifying the stock table
The keys of the dictionary work as the columns of the Stock table
The keys map to another dictionary which contains keys 
  spec: Gives the specification for the column
  name: Gives the full name for the column

Note that since Python 3.7 the order of the keys should
remain constant and thus this is the order in which the 
columns are specified
"""
stock_map = {"ticker": {"spec": "TEXT PRIMARY KEY", 
                        "name": "Ticker"},
             "lastUpdate": {"spec": "TEXT NOT NULL",
                            "name": "Last updated"},
             "exchange": {"spec": "TEXT NOT NULL",
                          "name": "Stock exchange"},
             "lastPrice": {"spec": "REAL",
                            "name": "Last price"},
             "currency": {"spec": "TEXT", 
                           "name": "Currency"},
             "drift": {"spec": "REAL",
                       "name": "Computed drift"},
             "vol": {"spec": "REAL",
                     "name": "Computed mean"},
             "marketCap": {"spec", "INTEGER",
                           "name", "Market Cap"},
             "eps": {"spec": "REAL",
                     "name": "EPS"},
             "PE": {"spec": "REAL",
                    "name": "P/E"},
             "DE": {"spec": "REAL",
                    "name": "D/E"},
             "div": {"spec": "REAL",
                     "name": "Dividend"},
             "divYield": {"spec": "REAL",
                          "name": "Dividend yield"},
             "beta": {"spec": "REAL",
                      "name": "Beta"}}

"""
Dictionary specifying the option table. 
Defined similarly to stock_map
"""
option_map = {"symbol": {"spec": "TEXT PRIMARY KEY",
                         "name": "Option symbol"},
              "underlying": {"spec": "TEXT NOT NULL",
                             "name": "Underlying asset"},
              "type": {"spec": "TEXT NOT NULL",
                       "name": "Option type"},
              "lastUpdate": {"spec": "TEXT NOT NULL",
                             "name": "Last updated"},
              "lastPrice": {"spec": "REAL",
                            "name": "Last price"},
              "strike": {"spec": "REAL",
                         "name": "Strike price"},
              "maturity": {"spec": "TEXT",
                           "name": "Maturity"}}

"""
Dictionary specifying the income statement table. 
Defined similarly to stock_map except the 'name'
values should correspond to the ones in Yahoo Finance
and thus used in the API
"""
incomeStmt_map = {"ticker": {"spec": "TEXT PRIMARY KEY",
                             "name": "Ticker"},
                  "lastUpdate": {"spec": "TEXT NOT NULL",
                                  "name": "Last updated"},
                  "dateIndex": {"spec": "TEXT NOT NULL",
                                "name": "Report dates"},
                  "totRevenue": {"spec": "TEXT",
                                 "name": "Total Revenue"},
                  "costRevenue": {"spec": "TEXT",
                                  "name": "Cost of Revenue"},
                  "grossProfit": {"spec": "TEXT",
                                  "name": "Gross Profit"},
                  "opExpense": {"spec": "TEXT",
                                "name": "Operating Expense"},
                  "opIncome": {"spec": "TEXT",
                                "name": "Operating Income"},
                  "nnoiIncomeExp": {"spec": "TEXT",
                                    "name": "Net Non Operating Interest Income Expense"},
                  "othIncomeExp": {"spec": "TEXT",
                                   "name": "Other Income Expense"},
                  "pretaxIncome": {"spec": "TEXT",
                                   "name": "Pretax Income"},
                  "taxProvision": {"spec": "TEXT",
                                   "name": "Tax Provision"},
                  "efeinoTax": {"spec": "TEXT",
                                "name": "Earnings from Equity Interest Net of Tax"},
                  "nics": {"spec": "TEXT",
                           "name": "Net Income Common Stockholders"},
                  "dilutedNI": {"spec": "TEXT",
                                "name": "Diluted NI Available to Com Stockholders"},
                  "basicEPS": {"spec": "TEXT",
                               "name": "Basic EPS"},
                  "dilutedEPS": {"spec": "TEXT",
                                 "name": "Diluted EPS"},
                  "bAvgShares": {"spec": "TEXT",
                                 "name": "Basic Average Shares"},
                  "dAvgShares": {"spec": "TEXT",
                                 "name": "Diluted Average Shares"},
                  "totOpIncome": {"spec": "TEXT",
                                  "name": "Total Operating Income as Reported"},
                  "totExpense": {"spec": "TEXT",
                                 "name": "Total Expenses"},
                  "netIncome": {"spec": "TEXT",
                                "name": "Net Income from Continuing & Discontinued Operation"},
                  "normIncome": {"spec": "TEXT",
                                 "name": "Normalized Income"},
                  "intIncome": {"spec": "TEXT",
                                "name": "Interest Income"},
                  "intExpense": {"spec": "TEXT",
                                 "name": "Interest Expense"},
                  "netIntInc": {"spec": "TEXT",
                                "name": "Net Interest Income"},
                  "ebit": {"spec": "TEXT",
                           "name": "EBIT"},
                  "ebitda": {"spec": "TEXT",
                             "name": "EBITDA"},
                  "recCostOfRev": {"spec": "TEXT",
                                   "name": "Reconciled Cost of Revenue"},
                  "recDepr": {"spec": "TEXT",
                              "name": "Reconciled Depreciation"},
                  "netContInc": {"spec": "TEXT",
                                 "name": "Net Income from Continuing Operation Net Minority Interest"},
                  "totUnusual": {"spec": "TEXT",
                                 "name": "Total Unusual Items"},
                  "normEbitda": {"spec": "TEXT",
                                 "name": "Normalized EBITDA"},
                  "calcTaxRate": {"spec": "TEXT",
                                  "name": "Tax Rate for Calcs"},
                  "teuItems": {"spec": "TEXT",
                               "name": "Tax Effect of Unusual Items"}}

"""
Dictionary specifying the balance sheet table. 
Defined similarly to incomeStmt_map
"""
balanceSheet_map = {"ticker": {"spec": "TEXT PRIMARY KEY",
                               "name": "Ticker"},
                    "lastUpdate": {"spec": "TEXT NOT NULL",
                                   "name": "Last updated"},
                    "dateIndex": {"spec": "TEXT NOT NULL",
                                  "name": "Report dates"},
                    "totAssets": {"spec": "TEXT",
                                  "name": "Total Assets"},
                    "totLiab": {"spec": "TEXT",
                                "name": "Total Liabilities Net Minority Interest"},
                    "totEquity": {"spec": "TEXT",
                                  "name": "Total Equity Gross Minority Interest"},
                    "totCap": {"spec": "TEXT",
                               "name": "Total Capitalization"},
                    "csEquity": {"spec": "TEXT",
                                 "name": "Common Stock Equity"},
                    "capLeaseObl": {"spec": "TEXT",
                                    "name": "Capital Lease Obligations"},
                    "netTangAssets": {"spec": "TEXT",
                                      "name": "Net Tangible Assets"},
                    "workingCap": {"spec": "TEXT",
                                   "name": "Working Capital"},
                    "investedCap": {"spec": "TEXT",
                                    "name": "Invested Capital"},
                    "tangBookVal": {"spec": "TEXT",
                                    "name": "Tangible Book Value"},
                    "totDebt": {"spec": "TEXT",
                                "name": "Total Debt"},
                    "netDebt": {"spec": "TEXT",
                                "name": "Net Debt"},
                    "shareIssued": {"spec": "TEXT",
                                    "name": "Share Issued"}}

"""
Dictionary specifying the cash flow statement table. 
Defined similarly to incomeStmt_map
"""
cashFlowStmt_map = {"ticker": {"spec": "TEXT PRIMARY KEY",
                               "name": "Ticker"},
                    "lastUpdate": {"spec": "TEXT NOT NULL",
                                   "name": "Last updated"},
                    "dateIndex": {"spec": "TEXT NOT NULL",
                                  "name": "Report dates"},
                    "opCashFlow": {"spec": "TEXT",
                                   "name": "Operating Cash Flow"},
                    "invCashFlow": {"spec": "TEXT",
                                    "name": "Investing Cash Flow"},
                    "finCashFlow": {"spec": "TEXT",
                                    "name": "Financing Cash Flow"},
                    "endCashPos": {"spec": "TEXT",
                                   "name": "End Cash Position"},
                    "capExp": {"spec": "TEXT",
                               "name": "Capital Expenditure"},
                    "issCap": {"spec": "TEXT",
                               "name": "Issuance of Capital Stock"},
                    "issDebt": {"spec": "TEXT",
                                "name": "Issuance of Debt"},
                    "repDebt": {"spec": "TEXT",
                                "name": "Repayment of Debt"},
                    "repStock": {"spec": "TEXT",
                                 "name": "Repurchase of Capital Stock"},
                    "freeCashFlow": {"spec": "TEXT",
                                     "name": "Free Cash Flow"}}
