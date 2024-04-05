# Module for main stock analysis framework

## Basics

Module containing the needed classes and functions for the computational side of the stock analysis toolshed
The modules main focus is on classes Stock, StockAPI, IncomeStmt, BalanceSheet, CashFlowStmt and Option. These are
described below: 

- Stock class is most important and does most of the heavy lifting. It also contains the company specific 
instances of StockAPI, IncomeStmt, BalanceSheet and CashFlowStmt. 

- StockAPI is an abstract base class for accessing financial information through some vendor. Currently, only implemented 
vendor is Yahoo Finance in class YahooAPI. 

- Classes IncomeStmt, BalanceSheet and CashFlowStmt as their name suggest hold the financial data for a given company. Potentially in the future there might be a need to
discern between reporting standards, but for now we use the one Yahoo Finance uses.

- Option class is also a abstract base class for different option
types (EuropeanPut, EuropeanCall, ...). 

## Database schema

The data once retrieved is stored in a database. The database consists of tables
(Note that in the financial reporting tables the yearly values can be found as ':' separated string of values)

- stock: Table for main stock information. Consists of columns:
  - ticker: The ticker symbol as TEXT. Works as the primary key
  - lastUpdate: The date for the last update as TEXT NOT NULL
  - lastPrice: The price of the stock at last update as REAL
  - currency: The currency used as TEXT
  - exchange: The exchange on which the stock is traded as TEXT
  - drift: The last computed drift as REAL
  - vol: The last computed volatility as REAL
  - marketCap: The market capitalization as INTEGER
  - eps: The earnings per share as REAL
  - PE: The price to earnings as REAL
  - DE: The debt to earnings as REAL
  - div: The dividend as REAL
  - divYield: The dividend yield as REAL
  - beta: The beta of the stock as a REAL

- option: Table for holding information of options
  - symbol: The option symbol as TEXT. Works as the primary key
  - underlying: The ticker of the underlying asset as TEXT NOT NULL
  - type: Describes the type of the option as TEXT NOT NULL
  - lastUpdate: The date for the last update as TEXT NOT NULL
  - lastPrice: The value of the option when last updated as REAL
  - strike: The strike price of the option as REAL
  - maturity: The date of expiration for the option as TEXT

- incomeStmt: Table holding the income stamement for a company
  - ticker: The ticker symbol as TEXT. Works as the primary key
  - lastUpdate: The date for the last update as TEXT NOT NULL
  - dateIndex: The years for which the values are found as TEXT NOT NULL
  - unit: The unit (e.g. thousands) with which the numbers are shown as TEXT
  - totRevenue: The total revenue as TEXT
  - costRevenue: The cost of revenue as TEXT
  - grossProfit: The gross profit as TEXT
  - opExpense: The operating expense as TEXT
  - opIncome: The operating income as TEXT
  - nnoiIncomeExp: The net operating interest income expense as TEXT
  - othIncomeExp: The other income expense as TEXT
  - pretaxIncome: The pretax income as TEXT
  - taxProvision: The tax provision as TEXT
  - efeinoTax: The earnings from equity interest net of tax as TEXT
  - nics: The net income of common stockholders as TEXT
  - dilutedNI: The diluted NI available to common stockholders as TEXT
  - basicEPS: The basic earnings per share as TEXT
  - dilutedEPS: The diluted EPS as TEXT
  - bAvgShares: The basic average shares outstanding as TEXT
  - dAvgShares: The diluted average shares outstanding as TEXT
  - totOpIncome: The reported total operating income as TEXT
  - totExpense: The total expenses as TEXT
  - netIncome: The net income from continuing and discontinued operations as TEXT
  - normIncome: The normalized income as TEXT
  - intIncome: The interest income as TEXT
  - intExpense: The interest expense as TEXT
  - netIntInc: The net interest income as TEXT
  - ebit: The EBIT as TEXT
  - ebitda: The EBITDA as TEXT
  - recCostOfRev: The reconciled cost of revenue as TEXT
  - recDepr: The reconciled deprecation as TEXT
  - netContInc: The net income from continuing operation net minority interest as TXT
  - totUnusual: The total unusual items as TEXT
  - normEbitda: The normalized EBITDA as TEXT
  - calcTaxRate: The tax rate used for calculations as TEXT
  - teuItems: The tax effect of unusual items as TEXT

- balanceSheet: Table holding the balance sheet for a company
  - ticker: The ticker symbol as TEXT. Works as the primary key
  - lastUpdate: The date for the last update as TEXT NOT NULL
  - dateIndex: The years for which the values are found as TEXT NOT NULL
  - unit: The unit (e.g. thousands) with which the numbers are shown as TEXT
  - totAssets: The total assets as TEXT
  - totLiab: The total liabilities net minority interest as TEXT
  - totEquity: The total equity gross minority interest as TEXT
  - totCap: The total capitalization as TEXT
  - csEquity: The common stock equity as TEXT
  - capLeaseObl: The capital lease obligations as TEXT
  - netTangAssets: The net tangible assets as TEXT
  - workingCap: The working capital as TEXT
  - investedCap: The invested capital as TEXT
  - tangBookVal: The tangible book value as TEXT
  - totDebt: The total debt as TEXT
  - netDebt: The net debt as TEXT
  - shareIssued: The number of shares issued as TEXT

- cashFlowStmt: Table for holding the cash flow statement for a company
  - ticker: The ticker symbol as TEXT. Works as the primary key
  - lastUpdate: The date for the last update as TEXT NOT NULL
  - dateIndex: The years for which the values are found as TEXT NOT NULL
  - unit: The unit (e.g. thousands) with which the numbers are shown as TEXT
  - opCashFlow: The operating cash flow as TEXT
  - invCashFlow: The investing cash flow as TEXT
  - finCashFlow: The financing cash flow as TEXT
  - endCashPos: The end cash position as TEXT
  - capExp: The capital expenditure as TEXT
  - issCap: The issuance of new capital stock as TEXT
  - issDebt: The issuance of new debt as TEXT
  - repDebt: The repayment of old debt as TEXT
  - repStock: The repurchase of capital stock as TEXT
  - freeCashFlow: The free cash flow as TEXT

The tables are also specified in file schema.py