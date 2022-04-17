import numpy as np
import pandas as pd 

# Lista de los campos a los que se le ha aplicado el fix trivial
trivial_fix_list = list({"Other Liabilities", "Preferred Stock", "Common Stock", "Tax Assets", "Tax Payable", "Capital Lease Obligations", "Common Stock Repurchased", "Common Stock Issued",
                    "Dividends Paid", "Deferred Income Tax", "Account Recievable", "Interest Income ", "Accounts Receivable", "Other Expenses", "Stock Based Compensation", "Deferred Income Tax",
                    "Interest Expense", "Other Investing Activities", "Accounts Payable", "PP&E", "Deferred Tax Liabilities", "Purchases of Investments", "Sales/Maturities of Investments","Investments",
                    "Deferred Revenue", "Other Assets", "Acquisitions Net", "Inventory", "Short-Term Debt", "Debt Repayment", "Long-Term Debt", "Research and Development Exp.", "Effect of Forex Changes on Cash", "Other Liabilities"
                    "Interest Income ", "Other Working Capital", "Short-Term Investments"})

core_columns = ["Revenue", "Gross Profit", "Operating Income","Income Tax Expense (Gain)", "Net Income", "Total Assets", "Total Liabilities", "Total Stockholders Equity"]



def calculateGrowthMetrics(df, columns):
    for column in columns:
        df[column+" growth yy"] = df[column] / df[column].shift(1) - 1
        df[column+" growth 3y. av."] = (df[column+" growth yy"] + df[column+" growth yy"].shift(1) + df[column+" growth yy"].shift(2))  / 3
        df[column+" growth 5y. av."] = (df[column+" growth yy"] + df[column+" growth yy"].shift(1) + df[column+" growth yy"].shift(2) + df[column+" growth yy"].shift(3) + df[column+" growth yy"].shift(4))  / 5
        df[column+" growth 10y. av."] = (df[column+" growth yy"] + df[column+" growth yy"].shift(1) + df[column+" growth yy"].shift(2) + df[column+" growth yy"].shift(3) + df[column+" growth yy"].shift(4) + df[column+" growth yy"].shift(5) + df[column+" growth yy"].shift(6) + df[column+" growth yy"].shift(7) + df[column+" growth yy"].shift(8) + df[column+" growth yy"].shift(9) + df[column+" growth yy"].shift(10))  / 10
        df[column +" cagr"] = (df[column].iloc[-1] / df[column].iloc[0]) ** (1/df.shape[0]) - 1
    return df.T


def clean_string_to_numeric(list_of_strings):
    # Takes a list of strings and returns a cleaned list
    # safe to convert to numeric
    res = []
    for string in list_of_strings:
        string = string.replace(",", "")
        string = string.replace("- -", "")
        string = string.replace("(", "-")
        string = string.replace(")", "")
        res.append(string)
    return res

def clean_and_reconstruct_fundamentals(df, reconstruct_df=True):
    
    # Cleaning
    df.drop(df.loc[["Income Statement", "SEC Link", "Balance Sheet", "Cash Flow Statement" ]].index, inplace=True)

    df.replace("- -", None, regex=True, inplace=True) 
    df.replace(",", "", regex=True, inplace=True) 
    df.replace("\(", "-",regex=True, inplace=True) 
    df.replace("\)", "",regex=True, inplace=True)
    df.replace("%", "",regex=True, inplace=True)

    df = df.apply(pd.to_numeric)   # convert all columns to numeric


    # Reconstructing
    if reconstruct_df:
        print("Reconstructing...")
        df = reconstructDf(df.T, trivial_fix=True)
    return df.T
    

def fundamental_calculator(fundamental_data): 
    fundamental_data = fundamental_data.T
    print(fundamental_data.columns)
    # ===================================================================================================================================
    #                                                     AÑADIR RATIOS
    # ===================================================================================================================================
    shares = fundamental_data["Weighted Avg. Shares Outs."]


    # Calculamos el FCF Ratio
    fundamental_data["FCF Ratio"] = fundamental_data["Free Cash Flow"] / fundamental_data["Revenue"]
    

    # ==========================================        MÉTRICAS PER SHARE        ===============================================
    # Calculamos el Revenue per Share
    fundamental_data["Revenue per Share"] = fundamental_data["Revenue"] / shares
    # Calculamos el FCF per share
    fundamental_data["FCF per share"] = fundamental_data["Free Cash Flow"] / shares
    # CAPEX per share
    fundamental_data["CAPEX per share"] = fundamental_data["CAPEX"] / shares

    # Book Value per share
    fundamental_data["Book value"]=fundamental_data["Total Stockholders Equity"].sub(fundamental_data["Preferred Stock"], fill_value=0)
    fundamental_data["Book value per share"] = fundamental_data["Book value"] / shares


    

    # =======================================     MÉTRICAS DE SALUD FINANCIERA       ===============================================
    # Calculamos total debt
    fundamental_data["Total Debt"] = fundamental_data["Short-Term Debt"].add(fundamental_data["Long-Term Debt"], fill_value=0)

    # Calculamos el Cash to Debt Ratio
    fundamental_data["Cash to Debt Ratio"] = fundamental_data["Cash and Cash Equivalents"] / fundamental_data["Total Debt"]
    if np.inf in fundamental_data["Cash to Debt Ratio"].values:
        fundamental_data["Cash to Debt Ratio"] = fundamental_data["Cash to Debt Ratio"].replace(np.inf, 99)



    # Calculamos el Cash & Short-Term Investments & Long Term Investments
    fundamental_data["Cash & Short-Term Investments & Long Term Investments"] = fundamental_data["Cash & Short-Term Investments"]+fundamental_data["Investments"]
    # Calculamos el Cash & Short-Term Investments & Long Term Investments to Debt Ratio
    fundamental_data["Cash & Short-Term Investments & Long Term Investments to Debt Ratio"] = fundamental_data["Cash & Short-Term Investments & Long Term Investments"] / fundamental_data["Total Debt"]
    if np.inf in fundamental_data["Cash & Short-Term Investments & Long Term Investments to Debt Ratio"].values:
        fundamental_data["Cash & Short-Term Investments & Long Term Investments to Debt Ratio"] = fundamental_data["Cash & Short-Term Investments & Long Term Investments to Debt Ratio"].replace(np.inf, 99)

        
    # Calculamos Net Debt
    fundamental_data["Net Debt"] = fundamental_data["Total Debt"] - fundamental_data["Cash & Short-Term Investments"]
    # Calculamos Net Debt minus Investments
    fundamental_data["Net Debt minus Investments"] = fundamental_data["Net Debt"] - fundamental_data["Investments"]

    # Calculamos el Working Capital
    fundamental_data["Working Capital"] = fundamental_data["Total Current Assets"] - fundamental_data["Total Current Liabilities"]

    # Calculamos Debt to EBITDA
    fundamental_data["Debt to EBITDA"] = fundamental_data["Total Debt"] / fundamental_data["EBITDA"]

    # Calculamos el Current Ratio
    fundamental_data["Current Ratio"] = fundamental_data["Total Current Assets"] / fundamental_data["Total Current Liabilities"]

    # Calculamos el Quick Ratio
    fundamental_data["Quick Ratio"] = (fundamental_data["Total Current Assets"] - fundamental_data["Inventory"])/ fundamental_data["Total Current Liabilities"]

    # Calculamos el Debt to Equity
    fundamental_data["Debt to Equity"] = fundamental_data["Total Debt"] / fundamental_data["Total Stockholders Equity"]

    # Calculamos el Debt to Assets
    fundamental_data["Debt to Assets"] = fundamental_data["Total Debt"] / fundamental_data["Total Assets"]

    # Calculamos el Liabilities to Assets
    fundamental_data["Liabilities to Assets"] = fundamental_data["Total Liabilities"] / fundamental_data["Total Assets"]


    # Calculamos el Interest Coverage
    fundamental_data["Interest Coverage"] = fundamental_data["EBITDA"] / fundamental_data["Interest Expense"]

    # Ponemos valor 99 para reflejar que la situación es buena
    if np.inf in fundamental_data["Interest Coverage"].values:
        fundamental_data["Interest Coverage"] = fundamental_data["Interest Coverage"].replace(np.inf, 99)
    elif -np.inf in fundamental_data["Interest Coverage"].values:
        fundamental_data["Interest Coverage"] = fundamental_data["Interest Coverage"].replace(-np.inf, np.nan)



    # =======================================     MÉTRICAS DE RENTABILIDAD       ===============================================
    # Calculamos el Return on Equity
    fundamental_data["Return on Equity"] = fundamental_data["Net Income"] / fundamental_data["Total Stockholders Equity"]

    # Calculamos el Return on Assets
    fundamental_data["Return on Assets"] = fundamental_data["Net Income"] / fundamental_data["Total Assets"]

    # Calculamos el ROIC
    fundamental_data["Tax Rate"] = fundamental_data["Income Tax Expense (Gain)"] / fundamental_data["Income Before Tax"]
    fundamental_data["NOPAT"] = fundamental_data["Operating Income"] * (1 - fundamental_data["Tax Rate"])
    fundamental_data["Invested Capital"] = fundamental_data["Total Stockholders Equity"].add(fundamental_data["Net Debt"], fill_value=0)
    fundamental_data["Return on Invested Capital"] = fundamental_data["NOPAT"] / fundamental_data["Invested Capital"]



    # =======================================     MÉTRICAS DE REINVERSIÓN      ===============================================
    # Calculamos el Plowback Ratio
    fundamental_data["Plowback Ratio"] = (fundamental_data["Net Income"] - fundamental_data["Dividends Paid"])/ fundamental_data["Net Income"]

    # Calculamos el Dividend & Repurchase / FCF
    fundamental_data["Dividend & Repurchase / FCF"] = (fundamental_data["Dividends Paid"] - fundamental_data["Common Stock Repurchased"] - fundamental_data["Common Stock Issued"]) / fundamental_data["Free Cash Flow"]

    # Calculamos el Dividend & Repurchase / EBITDA
    fundamental_data["Dividend & Repurchase / EBITDA"] = (fundamental_data["Dividends Paid"] - fundamental_data["Common Stock Repurchased"] - fundamental_data["Common Stock Issued"]) / fundamental_data["EBITDA"]



    # =======================================     MÉTRICAS DE CRECIMIENTO      ===============================================
    growth_cols = ["Revenue","Gross Profit","EBITDA","Operating Income","Net Income","EPS", "EPS Diluted", "Weighted Avg. Shares Outs.",
    "Weighted Avg. Shares Outs. Dil.", "Free Cash Flow", "FCF per share", "CAPEX per share", "Book value per share","Cash and Cash Equivalents",
    "Gross Profit Ratio", "EBITDA ratio", "Operating Income ratio", "Net Income Ratio", "FCF Ratio", "Return on Equity", "Return on Assets", "Return on Invested Capital", "Book value"]

    calculateGrowthMetrics(fundamental_data, growth_cols)

    return fundamental_data.T
    



def reconstructDf(df, trivial_fix =False):
    # Reconstruimos los fundamentales de una empresa a partir de otros elementos

    min_num_filas = 1

    if df.empty:
        print("El dataframe está vacío")
        return df
    
    if not df.isnull().values.any():
        print("El dataframe está en buen estado")
        return df

    if len(df.index) < min_num_filas:
        print("El dataframe tiene menos de {} filas".format(min_num_filas))
        return df
    
    # Los infinitos los tratamos como NaN
    if np.inf in df.values:
            df = df.replace(np.inf, np.nan)

    null_columns = []
    row_drop_set = set()

    for index, row in df.iterrows():
        # Vemos qué columna tiene un valor nulo y la guardamos
        null_columns = row[row.isna()].index.tolist()

        # Reparamos la columna con valor nulo
        for null_colum in null_columns:
            df.loc[index, null_colum] = applyFix(row, null_colum, visited_columns=[], trivial_fix=trivial_fix)

        
        null_columns.clear()

    if len(row_drop_set) > 0:
        df.drop(row_drop_set, inplace=True)

        # Al eliminar filas es posible que dejemos el dataframe vacío
        if df.empty:
            return df
        # O que no haya una cantidad de años representativa
        if len(df.index) < min_num_filas:
            return df


    df.drop(["General and Admin. Exp.","Selling and Marketing Exp."], axis=1, inplace=True)

    return df

def applyFix(row, col, visited_columns, trivial_fix=False):
    # Dependiendo de la columna, aplica un arreglo

    if col in visited_columns:
        print("Ya visitada. Saliendo...")
        return row[col]

    if row[col] == np.nan:
        print("No es nula. Saliendo...")
        return row[col]

    visited_columns.append(col)

    # Revenue
    if col == "Revenue":
        return  np.nan

    # COGS
    elif col == "COGS":
        repaired = try_repair_column(["Revenue", "Gross Profit"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] - row["Gross Profit"]

    # Gross Profit
    elif col == "Gross Profit":
        # Fix 1
        repaired = try_repair_column(["Revenue", "COGS"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] - row["COGS"]

        # Fix 2
        repaired = try_repair_column(["Revenue","Gross Profit Ratio"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] * row["Gross Profit Ratio"]
        
        else:
            return  np.nan

    # Gross Profit Ratio
    elif col == "Gross Profit Ratio":
        repaired = try_repair_column(["Revenue", "Gross Profit"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Gross Profit"] / row["Revenue"]

        else:
            return  np.nan

    # Other Assets
    elif col == "Other Assets":
        repaired = try_repair_column(["Total Assets", "Total Current Assets", "Total Non-Current Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Assets"] - row["Total Current Assets"] - row["Total Non-Current Assets"]
    
    # Selling and Marketing Exp.
    elif col == "Selling and Marketing Exp.":
        repaired = try_repair_column(["Selling, G&A Exp.", "General and Admin. Exp."],row, visited_columns, trivial_fix)

        if repaired:
            return row["Selling, G&A Exp."] - row["General and Admin. Exp."]
        else:
            return np.nan

    # Acquisitions Net
    elif col == "Acquisitions Net":
        repaired = try_repair_column(["CAPEX", "Purchases of Investments", "Sales/Maturities of Investments", "Other Investing Activities", "Cash Used for Investing Activities"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Cash Used for Investing Activities"] - row["CAPEX"] - row["Purchases of Investments"] - row["Sales/Maturities of Investments"] - row["Other Investing Activities"] 
        
    # Minority Interest
    elif col == "Minority Interest":
        repaired = try_repair_column(["Total Liab.&Stockhold. Equity", "Total Liabilities & Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Liabilities & Equity"] - row["Total Liab.&Stockhold. Equity"]

    # Deferred Tax Liabilities
    elif col == "Deferred Tax Liabilities":
        repaired = try_repair_column(["Long-Term Debt", "Deferred Revenue", "Other Non-Current Liabilities", "Total Non-Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Liabilities"] - row["Long-Term Debt"] - row["Deferred Revenue"] - row["Other Non-Current Liabilities"]

    # Investments
    elif col == "Investments":
        repaired = try_repair_column(["PP&E", "Goodwill", "Intangible Assets", "Tax Assets", "Other Non-Current Assets", "Total Non-Current Assets"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Non-Current Assets"] - row["PP&E"] - row["Goodwill"] - row["Intangible Assets"] - row["Tax Assets"] - row["Other Non-Current Assets"]
    
    # Short-Term Investments
    elif col == "Short-Term Investments":
        repaired = try_repair_column(["Cash and Cash Equivalents", "Cash & Short-Term Investments"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash & Short-Term Investments"] - row["Cash and Cash Equivalents"]

    # Deferred Revenue
    elif col == "Deferred Revenue":
        repaired = try_repair_column(["Long-Term Debt", "Deferred Tax Liabilities", "Other Non-Current Liabilities", "Total Non-Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Liabilities"] - row["Long-Term Debt"] - row["Deferred Tax Liabilities"] - row["Other Non-Current Liabilities"]

    # Research and Development Exp.
    elif col == "Research and Development Exp.":
        repaired = try_repair_column(["Selling, G&A Exp.", "Operating Expenses", "Other Expenses"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Operating Expenses"] -  row["Selling, G&A Exp."] - row["Other Expenses"]

    # Effect of Forex Changes on Cash
    elif col == "Effect of Forex Changes on Cash":
        repaired = try_repair_column(["Cash Provided by Operating Activities", "Cash Used/Provided by Financing Activities", "Cash Used for Investing Activities", "Net Change In Cash"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Change In Cash"] - row["Cash Provided by Operating Activities"] - row["Cash Used/Provided by Financing Activities"] - row["Cash Used for Investing Activities"]

    # Sales/Maturities of Investments
    elif col == "Sales/Maturities of Investments":
        repaired = try_repair_column(["CAPEX", "Acquisitions Net", "Purchases of Investments", "Other Investing Activities", "Cash Used for Investing Activities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash Used for Investing Activities"] - row["CAPEX"] - row["Acquisitions Net"] - row["Purchases of Investments"] - row["Other Investing Activities"]

    # Purchases of Investments
    elif col == "Purchases of Investments":
        repaired = try_repair_column(["CAPEX", "Acquisitions Net", "Sales/Maturities of Investments", "Other Investing Activities", "Cash Used for Investing Activities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash Used for Investing Activities"] - row["CAPEX"] - row["Acquisitions Net"] - row["Sales/Maturities of Investments"] - row["Other Investing Activities"]

    # Goodwill
    elif col == "Goodwill":
        # Fix 1
        repaired = try_repair_column(["PP&E", "Intangible Assets", "Investments", "Tax Assets", "Other Non-Current Assets", "Total Non-Current Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Assets"] - row["PP&E"] - row["Intangible Assets"] - row["Investments"] - row["Tax Assets"] - row["Other Non-Current Assets"]
        
    # Inventory
    elif col == "Inventory":
        repaired = try_repair_column(["Cash & Short-Term Investments", "Net Receivables", "Other Current Assets", "Total Current Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Current Assets"] - row["Cash & Short-Term Investments"] - row["Net Receivables"] - row["Other Current Assets"]
        
    # Intangible Assets
    elif col == "Intangible Assets":
        repaired = try_repair_column(["Goodwill", "Investments", "PP&E", "Tax Assets", "Other Non-Current Assets", "Total Non-Current Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Assets"] - row["Goodwill"] - row["Investments"] - row["PP&E"] - row["Tax Assets"] - row["Other Non-Current Assets"]

    # Debt Repayment
    elif col == "Debt Repayment":
        repaired = try_repair_column(["Common Stock Issued", "Common Stock Repurchased", "Dividends Paid", "Other Financing Activities", "Cash Used/Provided by Financing Activities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash Used/Provided by Financing Activities"] - row["Common Stock Issued"] - row["Common Stock Repurchased"] - row["Dividends Paid"] - row["Other Financing Activities"]
        
    # Short-Term Debt
    elif col == "Short-Term Debt":
        repaired = try_repair_column(["Accounts Payable", "Deferred Revenue", "Other Current Liabilities", "Total Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Current Liabilities"] - row["Accounts Payable"] - row["Deferred Revenue"] - row["Other Current Liabilities"]

    # Long-Term Debt
    elif col == "Long-Term Debt":
        repaired = try_repair_column(["Deferred Revenue", "Deferred Tax Liabilities", "Other Non-Current Liabilities", "Total Non-Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Liabilities"] - row["Deferred Revenue"] - row["Deferred Tax Liabilities"] - row["Other Non-Current Liabilities"]

    # Other Non-Current Liabilities
    elif col == "Other Non-Current Liabilities":
        repaired = try_repair_column(["Long-Term Debt", "Deferred Tax Liabilities", "Other Non-Current Liabilities", "Total Non-Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Non-Current Liabilities"] - row["Long-Term Debt"] - row["Deferred Revenue"] - row["Deferred Tax Liabilities"]
        
    # Cash Used/Provided by Financing Activities
    elif col == "Cash Used/Provided by Financing Activities":
        repaired = try_repair_column(["Debt Repayment", "Common Stock Issued", "Common Stock Repurchased", "Dividends Paid", "Other Financing Activities"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Debt Repayment"] + row["Common Stock Issued"] + row["Common Stock Repurchased"] + row["Dividends Paid"] + row["Other Financing Activities"]
        
    # Other Compreh. Income(Loss)
    elif col == "Other Compreh. Income(Loss)":
        repaired = try_repair_column(["Preferred Stock", "Common Stock", "Retained Earnings", "Other Total Stockhold. Equity", "Total Stockholders Equity"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Stockholders Equity"] - row["Preferred Stock"] - row["Common Stock"] - row["Retained Earnings"] - row["Other Total Stockhold. Equity"]  

    # Net Receivables
    elif col == "Net Receivables":
        repaired = try_repair_column(["Cash & Short-Term Investments", "Inventory", "Other Current Assets", "Total Current Assets"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Current Assets"] - row["Cash & Short-Term Investments"] - row["Inventory"] - row["Other Current Assets"]
    
    # General and Admin. Exp.
    elif col == "General and Admin. Exp.":
        repaired = try_repair_column(["Selling and Marketing Exp.", "Selling, G&A Exp."],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Selling, G&A Exp."] - row["Selling and Marketing Exp."]
        
    # Total Non-Current Liabilities
    elif col == "Total Non-Current Liabilities":
        repaired = try_repair_column(["Long-Term Debt", "Deferred Tax Liabilities", "Other Non-Current Liabilities", "Deferred Revenue"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Long-Term Debt"] + row["Other Non-Current Liabilities"] + row["Deferred Revenue"] + row["Deferred Tax Liabilities"]
    
    # Selling, G&A Exp.
    elif col == "Selling, G&A Exp.":
        repaired = try_repair_column(["Research and Development Exp.", "Operating Expenses", "Other Expenses"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Operating Expenses"]  - row["Research and Development Exp."] - row["Other Expenses"]
    
    # CAPEX
    elif col == "CAPEX":
        repaired = try_repair_column(["Acquisitions Net", "Purchases of Investments", "Sales/Maturities of Investments", "Other Investing Activities", "Cash Used for Investing Activities"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Cash Used for Investing Activities"] - row["Acquisitions Net"] - row["Purchases of Investments"] - row["Sales/Maturities of Investments"] - row["Other Investing Activities"]

    # Total Other Income Exp.(Gains)
    elif col == "Total Other Income Exp.(Gains)":
        repaired = try_repair_column(["Operating Income", "Income Before Tax"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Income Before Tax"] - row["Operating Income"]

    # COGS and Expenses
    elif col == "COGS and Expenses":
        repaired = try_repair_column(["COGS", "Operating Expenses"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["COGS"] + row["Operating Expenses"]

    # Income Tax Expense (Gain)
    elif col == "Income Tax Expense (Gain)":
        repaired = try_repair_column(["Income Before Tax", "Net Income"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Income Before Tax"] - row["Net Income"]

    # Other Non-Current Assets
    elif col == "Other Non-Current Assets":
        repaired = try_repair_column(["PP&E", "Goodwill", "Intangible Assets", "Investments", "Tax Assets","Total Non-Current Assets"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Non-Current Assets"] - row["PP&E"] - row["Goodwill"] - row["Intangible Assets"] - row["Investments"] - row["Tax Assets"]
    
    # Other Current Assets
    elif col == "Other Current Assets":
        repaired = try_repair_column(["Cash & Short-Term Investments", "Inventory", "Net Receivables", "Total Current Assets"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Current Assets"] - row["Cash & Short-Term Investments"] - row["Inventory"] - row["Net Receivables"]

    # Other Current Liaibilities
    elif col == "Other Current Liabilities":
        repaired = try_repair_column(["Accounts Payable", "Short-Term Debt", "Deferred Revenue", "Total Current Liabilities"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Total Current Liabilities"] - row["Accounts Payable"] - row["Short-Term Debt"] - row["Deferred Revenue"]

    # Total Non-Current Assets
    elif col == "Total Non-Current Assets":
        repaired = try_repair_column(["PP&E", "Goodwill", "Intangible Assets", "Investments", "Tax Assets", "Other Non-Current Assets", "Tax Assets"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Tax Assets"] + row["PP&E"] + row["Goodwill"] + row["Intangible Assets"] + row["Investments"] + row["Tax Assets"] + row["Other Non-Current Assets"]

    # EBITDA
    elif col == "EBITDA":
        # Fix 1
        repaired = try_repair_column(["Interest Expense", "Depreciation and Amortization", "Operating Income", "Total Other Income Exp.(Gains)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Interest Expense"] + row["Depreciation and Amortization"] + row["Operating Income"] + row["Total Other Income Exp.(Gains)"]
        
        # Fix 2
        repaired = try_repair_column(["EBITDA ratio", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] * row["EBITDA ratio"]

    # Depreciation and Amortization
    elif col == "Depreciation and Amortization":
        repaired = try_repair_column(["Interest Expense", "EBITDA", "Operating Income", "Total Other Income Exp.(Gains)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["EBITDA"] - row["Interest Expense"] - row["Operating Income"] - row["Total Other Income Exp.(Gains)"]
        
    # Other Financing Activities
    elif col == "Other Financing Activities":
        repaired = try_repair_column(["Debt Repayment", "Common Stock Issued", "Common Stock Repurchased", "Dividends Paid", "Cash Used/Provided by Financing Activities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash Used/Provided by Financing Activities"] - row["Debt Repayment"] - row["Common Stock Issued"] - row["Common Stock Repurchased"] - row["Dividends Paid"]
    
    # Other Total Stockhold. Equity
    elif col == "Other Total Stockhold. Equity":
        repaired = try_repair_column(["Total Stockholders Equity", "Preferred Stock", "Common Stock", "Retained Earnings","Other Compreh. Income(Loss)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Stockholders Equity"] - row["Preferred Stock"] - row["Common Stock"] - row["Retained Earnings"] - row["Other Compreh. Income(Loss)"]

    # Operating Income
    elif col == "Operating Income":
        # Fix 1
        repaired = try_repair_column(["Interest Expense", "Depreciation and Amortization", "EBITDA", "Total Other Income Exp.(Gains)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["EBITDA"] - row["Interest Expense"] - row["Depreciation and Amortization"] - row["Total Other Income Exp.(Gains)"]
        
        # Fix 2
        repaired = try_repair_column(["Operating Income ratio", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] * row["Operating Income ratio"]
        
        # Fix 3
        repaired = try_repair_column(["Gross Profit", "Operating Expenses"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Gross Profit"] - row["Operating Expenses"]
        
        # Fix 4
        repaired = try_repair_column(["Income Before Tax", "Total Other Income Exp.(Gains)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Income Before Tax"] + row["Total Other Income Exp.(Gains)"]

    # Operating Income ratio
    elif col == "Operating Income ratio":
        repaired = try_repair_column(["Operating Income", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Operating Income"] / row["Revenue"]

    # Cash at the End of Period
    elif col == "Cash at the End of Period":
        repaired = try_repair_column(["Cash at the Beginning of Period", "Net Change In Cash"],row, visited_columns, trivial_fix)
        
        if repaired:
            return row["Cash at the Beginning of Period"] + row["Net Change In Cash"]

    # Retained Earnings
    elif col == "Retained Earnings":
        repaired = try_repair_column(["Preferred Stock", "Common Stock", "Other Compreh. Income(Loss)","Other Total Stockhold. Equity", "Total Stockholders Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Stockholders Equity"] - row["Preferred Stock"] - row["Common Stock"] - row["Other Compreh. Income(Loss)"] - row["Other Total Stockhold. Equity"]

    # Cash Used for Investing Activities
    elif col == "Cash Used for Investing Activities":
        # Fix 1
        repaired = try_repair_column(["CAPEX", "Acquisitions Net", "Purchases of Investments", "Sales/Maturities of Investments", "Other Investing Activities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["CAPEX"] + row["Acquisitions Net"] + row["Purchases of Investments"] + row["Sales/Maturities of Investments"] + row["Other Investing Activities"]
        
    # Operating Expenses
    elif col == "Operating Expenses":
        # Fix 1
        repaired = try_repair_column(["Gross Profit", "Operating Income"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Gross Profit"] - row["Operating Income"]

        # Fix 2
        repaired = try_repair_column(["Research and Development Exp.", "Selling, G&A Exp.", "Other Expenses"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Research and Development Exp."] + row["Selling, G&A Exp."] + row["Other Expenses"]
        
    # Total Current Liaibilities
    elif col == "Total Current Liabilities":
        repaired = try_repair_column(["Accounts Payable", "Short-Term Debt", "Deferred Revenue", "Other Current Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Accounts Payable"] + row["Short-Term Debt"] + row["Deferred Revenue"] + row["Other Current Liabilities"]

    # Total Current Assets
    elif col == "Total Current Assets":
        repaired = try_repair_column(["Cash & Short-Term Investments", "Net Receivables", "Inventory","Other Current Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash & Short-Term Investments"] + row["Net Receivables"] + row["Inventory"] + row["Other Current Assets"]

    # Cash at the Beginning of Period
    elif col == "Cash at the Beginning of Period":
        repaired = try_repair_column(["Cash at the End of Period", "Net Change In Cash"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash at the End of Period"] - row["Net Change In Cash"]
    
    # Net Change In Cash
    elif col == "Net Change In Cash":
        repaired = try_repair_column(["Cash at the Beginning of Period", "Cash at the End of Period"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash at the End of Period"] - row["Cash at the Beginning of Period"]
    
    # Income Before Tax
    elif col == "Income Before Tax":
        # Fix 1
        repaired = try_repair_column(["Net Income", "Interest Expense"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income"] + row["Interest Expense"]

        # Fix 2
        repaired = try_repair_column(["Operating Income", "Total Other Income Exp.(Gains)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Operating Income"] - row["Total Other Income Exp.(Gains)"]

        # Fix 3
        repaired = try_repair_column(["Income Before Tax Ratio", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Revenue"] * row["Income Before Tax Ratio"]

    # Income Before Tax Ratio
    elif col == "Income Before Tax Ratio":
        repaired = try_repair_column(["Income Before Tax", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Income Before Tax"] / row["Revenue"]

    # Cash & Short-Term Investments
    elif col == "Cash & Short-Term Investments":
        repaired = try_repair_column(["Cash and Cash Equivalents","Short-Term Investments"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash and Cash Equivalents"] + row["Short-Term Investments"]

    # Cash and Cash Equivalents
    elif col == "Cash and Cash Equivalents":
        repaired = try_repair_column(["Cash & Short-Term Investments", "Short-Term Investments"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash & Short-Term Investments"] - row["Short-Term Investments"]
    
    # Cash Provided by Operating Activities
    elif col == "Cash Provided by Operating Activities":
        # Fix 1
        repaired = try_repair_column(["Effect of Forex Changes on Cash","Cash Used/Provided by Financing Activities", "Cash Used for Investing Activities", "Net Change In Cash"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Change In Cash"] - row["Effect of Forex Changes on Cash"] - row["Cash Used/Provided by Financing Activities"] - row["Cash Used for Investing Activities"]

        # Fix 2
        repaired = try_repair_column(["Net Income", "Depreciation and Amortization", "Deferred Income Tax", "Stock Based Compensation", "Change in Working Capital", "Other Non-Cash Items"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income"] + row["Depreciation and Amortization"] + row["Deferred Income Tax"] + row["Stock Based Compensation"] + row["Change in Working Capital"] + row["Other Non-Cash Items"]
    
    # Total Stockholders Equity
    elif col == "Total Stockholders Equity":
        repaired = try_repair_column(["Total Assets", "Total Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Assets"] - row["Total Liabilities"]
    
    # Free Cash Flow
    elif col == "Free Cash Flow":
        repaired = try_repair_column(["Cash Provided by Operating Activities", "CAPEX"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Cash Provided by Operating Activities"] + row["CAPEX"]

    # Total Assets
    elif col == "Total Assets":
        # Fix 1
        repaired = try_repair_column(["Total Current Assets", "Total Non-Current Assets", "Other Assets"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Current Assets"] + row["Total Non-Current Assets"] + row["Other Assets"]
        
        # Fix 2
        repaired = try_repair_column(["Total Liabilities", "Total Stockholders Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Stockholders Equity"] + row["Total Liabilities"]

    # Total Liabilities & Equity
    elif col == "Total Liabilities & Equity":
        repaired = try_repair_column(["Total Liabilities", "Total Stockholders Equity", "Minority Interest"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Liabilities"] + row["Total Stockholders Equity"] + row["Minority Interest"]

    # Total Liab.&Stockhold. Equity
    elif col == "Total Liab.&Stockhold. Equity":
        repaired = try_repair_column(["Total Liabilities", "Total Stockholders Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Liabilities"] + row["Total Stockholders Equity"]
    
    # Total Liabilities
    elif col == "Total Liabilities":
        # Fix 1
        repaired = try_repair_column(["Total Current Liabilities", "Total Non-Current Liabilities", "Other Liabilities"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Current Liabilities"] + row["Total Non-Current Liabilities"] + row["Other Liabilities"]

        # Fix 2
        repaired = try_repair_column(["Total Liabilities & Equity", "Minority Interest", "Total Stockholders Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Liabilities & Equity"] - row["Minority Interest"] - row["Total Stockholders Equity"]

        # Fix 3
        repaired = try_repair_column(["Total Liab.&Stockhold. Equity", "Total Stockholders Equity"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Total Liab.&Stockhold. Equity"] - row["Total Stockholders Equity"]

    # EPS
    elif col == "EPS":
        repaired = try_repair_column(["Net Income","Weighted Avg. Shares Outs."],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income"] / row["Weighted Avg. Shares Outs."]

    # EPS Diluted
    elif col == "EPS Diluted":
        repaired = try_repair_column(["Net Income","Weighted Avg. Shares Outs. Dil."],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income"] / row["Weighted Avg. Shares Outs. Dil."]
    
    # EBITDA ratio
    elif col == "EBITDA ratio":
        repaired = try_repair_column(["EBITDA", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["EBITDA"] / row["Revenue"]
    
    # Net Income Ratio
    elif col == "Net Income Ratio":
        repaired = try_repair_column(["Net Income", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income"] / row["Revenue"]

    # Net Income
    elif col == "Net Income":
        # Fix 1
        repaired = try_repair_column(["Income Before Tax", "Income Tax Expense (Gain)"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Income Before Tax"] - row["Income Tax Expense (Gain)"]
        
        # Fix 2
        repaired = try_repair_column(["Net Income Ratio", "Revenue"],row, visited_columns, trivial_fix)

        if repaired:
            return row["Net Income Ratio"] * row["Revenue"]
            

    # Aplicamos el fix trivial
    if trivial_fix and col in trivial_fix_list:
        return  0

    # No tenemos implementación
    else:
        return np.nan



def try_repair_column(columns_to_repair,row, visited_columns, trivial_fix):
    # Intenta reparar una columna (la principal) usando otras coumnas (las secundarias)
    # Intenta reparar las columnas secundarias llamando a applyFix
    # Si consigue reparar las necesarias, repara la columna principal

    for col_to_repair in columns_to_repair:            
        # Si es nula intentamos reparar
        if np.isnan(row[col_to_repair]):
            # Si es null pero ya la hemos visitado -> Se ha intentado reparar pero no se ha podido, ergo, tampoco podemos reparar la columna principal
            if col_to_repair in visited_columns:
                return False

            # Si la columna es nula y no la hemos visitado -> Intentamos repararla
            else:
                row[col_to_repair] = applyFix(row, col_to_repair, visited_columns, trivial_fix)
                # Volvemos a comprabar si la columna es nula
                if np.isnan(row[col_to_repair]):
                    return False

    return True