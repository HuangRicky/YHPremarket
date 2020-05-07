# YHPremarket
Yahoo Finance Pre-market

# Usage

Please see sample below:

	import YHPremarket as yhp
	d = yhp.yhparse_many(['SPY', 'USO', 'GOOG', 'AAPL'], verbose=True)
	print(d)
