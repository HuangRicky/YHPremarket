# YHPremarket
Yahoo Finance Pre-market

# Usage

Please see sample below:

	import YHPremarket as yhp
	import logging
	logger = logging.getLogger("YHPremarket")
	logger.setLevel(logging.INFO)
	fh = logging.FileHandler("file.log")
	logger.addHandler(fh)
	d = yhp.yhparse_many(['SPY', 'USO', 'GOOG', 'AAPL'], verbose=True)
	print(d)
