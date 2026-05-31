import stripe
from stripe import error
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import dotenv
import os
# Initialize FastAPI
dotenv.load_dotenv()  # Load environment variables from .env file
app = FastAPI()

# TODO: Replace with your actual Stripe Secret Key
stripe.api_key = os.getenv("a")

# Define the expected request body
class PaymentRequest(BaseModel):
    amount: int  # Stripe expects the amount in the smallest currency unit (e.g., paise for INR, cents for USD)
    currency: str = "inr"

@app.post("/create-payment-link")
async def create_payment_link(request: PaymentRequest):
    try:
        # Create a Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': request.currency,
                    'unit_amount': request.amount,
                    'product_data': {
                        'name': 'Zynking Order', # Customize this based on the actual purchase
                    },
                },
                'quantity': 1,
            }],
            mode='payment', # Use 'subscription' if you are setting up recurring payments
            
            # These URLs tell Stripe where to redirect the user after the payment finishes.
            # You should configure Deep Links in Flutter to catch these custom schemes.
            success_url='zynk://payment/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='zynk://payment-cancel',
        )
        
        # Return the generated webpage URL to the Flutter app
        return {"payment_url": session.url}
    
    except stripe.error.StripeError as e: # type: ignore
        # Handle specific Stripe errors securely
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")