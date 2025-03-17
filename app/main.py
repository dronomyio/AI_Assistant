  # In app/main.py
  from flask import Flask, session, redirect, request
  from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
  from werkzeug.security import generate_password_hash, check_password_hash

  app = Flask(__name__)
  app.secret_key = os.environ.get("SECRET_KEY")

  login_manager = LoginManager()
  login_manager.init_app(app)

  # Simple in-memory user store (use a database in production)
  users = {}

  class User(UserMixin):
      def __init__(self, id, email, password_hash, subscription=None):
          self.id = id
          self.email = email
          self.password_hash = password_hash
          self.subscription = subscription or {"status": "free"}

  @login_manager.user_loader
  def load_user(user_id):
      return users.get(user_id)

  @app.route('/register', methods=['POST'])
  def register():
      email = request.form.get('email')
      password = request.form.get('password')

      if email in [user.email for user in users.values()]:
          return jsonify({"error": "Email already exists"}), 400

      user_id = str(uuid.uuid4())
      users[user_id] = User(
          id=user_id,
          email=email,
          password_hash=generate_password_hash(password)
      )

      login_user(users[user_id])
      return redirect('/')

  @app.route('/login', methods=['POST'])
  def login():
      email = request.form.get('email')
      password = request.form.get('password')

      user = next((u for u in users.values() if u.email == email), None)
      if not user or not check_password_hash(user.password_hash, password):
          return jsonify({"error": "Invalid credentials"}), 401

      login_user(user)
      return redirect('/')

  @app.route('/api/query', methods=['POST'])
  @login_required
  def process_query():
      # Handle query processing
      # ...
  Implement Subscription Management with Stripe

  # In app/main.py
  import stripe
  stripe.api_key = os.environ.get("STRIPE_API_KEY")

  @app.route('/create-checkout-session', methods=['POST'])
  @login_required
  def create_checkout_session():
      tier = request.form.get('tier', 'basic')

      # Map tiers to Stripe price IDs
      price_ids = {
          'basic': 'price_xxxx',
          'professional': 'price_yyyy',
          'enterprise': 'price_zzzz'
      }

      checkout_session = stripe.checkout.Session.create(
          customer_email=current_user.email,
          success_url=request.host_url + 'success?session_id={CHECKOUT_SESSION_ID}',
          cancel_url=request.host_url + 'cancel',
          payment_method_types=['card'],
          mode='subscription',
          line_items=[{
              'price': price_ids[tier],
              'quantity': 1
          }],
          metadata={
              'user_id': current_user.id
          }
      )

      return redirect(checkout_session.url)

  @app.route('/webhook', methods=['POST'])
  def webhook():
      payload = request.get_data(as_text=True)
      sig_header = request.headers.get('Stripe-Signature')

      try:
          event = stripe.Webhook.construct_event(
              payload, sig_header, os.environ.get("STRIPE_WEBHOOK_SECRET")
          )
      except ValueError as e:
          return jsonify({"error": "Invalid payload"}), 400
      except stripe.error.SignatureVerificationError as e:
          return jsonify({"error": "Invalid signature"}), 400

      # Handle subscription events
      if event['type'] == 'customer.subscription.created':
          subscription = event['data']['object']
          user_id = subscription['metadata']['user_id']
          if user_id in users:
              users[user_id].subscription = {
                  "status": "active",
                  "tier": get_tier_from_subscription(subscription),
                  "current_period_end": subscription['current_period_end']
              }

      return jsonify({"status": "success"})

  Set Up Application Monitoring

  # In app/main.py
  import logging
  from opencensus.ext.flask.flask_middleware import FlaskMiddleware
  from opencensus.ext.azure.log_exporter import AzureLogHandler

  # Configure logging
  logging.basicConfig(level=logging.INFO)
  logger = logging.getLogger(__name__)

  if os.environ.get("APPINSIGHTS_CONNECTIONSTRING"):
      logger.addHandler(AzureLogHandler(
          connection_string=os.environ.get("APPINSIGHTS_CONNECTIONSTRING")
      ))

  # Initialize monitoring middleware
  middleware = FlaskMiddleware(
      app,
      exporter=AzureExporter(connection_string=os.environ.get("APPINSIGHTS_CONNECTIONSTRING"))
  )

  # Log API queries
  @app.route('/api/query', methods=['POST'])
  @login_required
  def process_query():
      query = request.json.get('query', '')

      logger.info(
          f"Query received",
          extra={
              "user_id": current_user.id,
              "subscription_tier": current_user.subscription.get("tier", "free"),
              "query_length": len(query)
          }
      )

      # Process query...
      # ...

      logger.info(
          f"Query processed",
          extra={
              "user_id": current_user.id,
              "processing_time_ms": processing_time,
              "response_length": len(answer)
          }
      )

      return jsonify({"answer": answer})


