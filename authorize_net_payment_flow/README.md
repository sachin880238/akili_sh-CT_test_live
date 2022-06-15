Credit Card Processing Using Authorize.net

If Account/CustomerProfileID = null (first credit card transaction for this customer)
- open new credit card window
- get card number, expiration date, and CCV code
- display all billing addresses with quotation billing address selected, allow editing the billing
		
address, selecting another billing address, or creating a new billing address
- send createCustomerProfileRequest
- evaluate response for problems
- save customerProflleId (Account table) and customer PaymentProfileId (new Card table)
- send createTransactionRequest
- evaluate response
- save amount, authorization code, and other details (Payment table)
If Account/CustomerProfileID ≠ null (previous credit card transactions)
- send getCustomerProfileRequest to get previous credit card numbers and expirations
- display credit cards with selection buttons
- If customer selects existing card
		
- customer has option to change billing address or expiration date but not card number
		
- send updateCustomerPaymentProfileRequest
		
- evaluate response
		
- send createTransactionRequest
		
- evaluate response
		
- save amount, authorization code, and other details (Payment table)
- If customer creates a new card
		
- open new credit card window
		
- get card number, expiration date, and CCV code
		
- display all billing addresses with quotation billing address selected, allow editing
			
the billing address, selecting another billing address, or creating a new
			billing address
		
- send createCustomerPaymentProfileRequest, get customerPaymentProfileId
		
- evaluate response
		
- send createTransactionRequest
		
- evaluate response
		
- save amount, authorization code, and other details (Payment table)
The invoicing process will require capture, refund, and void operations.
---------------

 
