# Configuration for Jupiter Edge+ AI Agent

# FOMO (Fear of Missing Out) Offer Configuration
# This offer is shown when customers are hesitant or not willing to continue

FOMO_OFFERS = {'default': {'enabled': True, 'title': '🎁 Limited Time Offer', 'message': "Since you're one of our early applicants, we're offering an EXCLUSIVE bonus: Get ₹500 worth of Jewels (₹100 cashback) credited instantly on your first transaction! This offer is valid only for applications completed in the next 48 hours.", 'urgency_text': '⏰ This exclusive bonus expires in 48 hours!', 'cta': "Don't miss out on this limited-time bonus. Would you like to complete your application now?"}, 'high_value': {'enabled': True, 'title': '🎁 Limited Time Offer', 'message': '1 year JioHotStar Subscription', 'urgency_text': '⏰ This exclusive bonus expires in 48 hours!', 'cta': "Don't miss out on this limited-time bonus. Would you like to complete your application now?"}, 'zero_fee_highlight': {'enabled': True, 'title': '🆓 Lifetime Free Card - Limited Slots', 'message': 'Quick heads up: We have limited slots left for our Lifetime Free Card offer. After this month, new applicants will have to pay ₹500 joining fee. You can secure your ZERO joining fee slot by completing your application today!', 'urgency_text': "⏳ Limited slots remaining - secure yours before it's too late!", 'cta': 'Would you like to reserve your lifetime free card slot now?'}, 'instant_approval': {'enabled': True, 'title': '⚡ Instant Approval - Available Now', 'message': "Good news! Your pre-qualification shows you're likely to get instant approval with a credit limit of up to ₹1,00,000. Complete your application in the next 2 hours to get instant approval and start using your card immediately!", 'urgency_text': '🚀 Instant approval window closes in 2 hours!', 'cta': 'Ready to get your card approved instantly?'}}

# Choose which offer to use
ACTIVE_FOMO_OFFER = "high_value"

# Trigger conditions - when to show FOMO offer
FOMO_TRIGGER_CONDITIONS = {'show_on_hesitation': True, 'show_on_decline': True, 'show_on_thinking': True, 'max_attempts': 1}

# App link for continuing application
APPLICATION_LINK = "https://jupiter.money/edge-plus-upi-rupay-credit-card/"
