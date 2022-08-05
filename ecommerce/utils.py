from datetime import datetime
from dateutil.relativedelta import *
import json
from django.conf import settings
from .models import Wallet, Source, Invoice, Line, CartItem
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeManager:
    '''
    This manager allows us to call a few of Stripe's endpoints. 
    '''
    def __init__(self, user, *args, **kwargs):
        self.user = user
        self.up = self.user.userprofile
        self.cart = self.user.cart
        self.amount = self.cart.amount()
        self.token = kwargs.get("token")
        self.source_id = kwargs.get("source_id")
        self.price_id = kwargs.get("price_id")
        self.invoice_id = kwargs.get("invoice_id")
        self.invoice_item_id = kwargs.get("invoice_item_id")
        self.tax_id = settings.STRIPE_TAX
        self.currency = self.user.wallet.currency
        self.description = 'Django demo'
        

    def stripe_id(self):
        wallet = self.wallet_object()
        if not wallet.stripe_id:
            self.post_profile()			
        return wallet.stripe_id

    def wallet_object(self):
        wallet, created = Wallet.objects.get_or_create(user = self.user)
        return wallet

    def source_object(self, id):
        source, created = Source.objects.get_or_create(stripe_id = id)
        if self.token:
            source.is_default = True
            source.save()
        wallet = self.wallet_object()
        wallet.sources.add(source)
        wallet.save()
        return source

    def line_object(self, id, item_obj):
        line, created = Line.objects.get_or_create(stripe_id = id)
        line.item = item_obj.item
        line.user = self.user
        line.quantity = item_obj.quantity
        line.sell_amount = item_obj.amount() / 100
        line.buy_amount = item_obj.amount() / 100
        line.amount_currency = self.wallet_object().currency
        line.save()
        return line

    def invoice_object(self, id, items, source_id):
        invoice, created = Invoice.objects.get_or_create(stripe_id = id)
        for item in items:
            invoice.lines.add(item)
            invoice.save()
        invoice.user = self.user
        invoice.source = Source.objects.get(stripe_id = source_id)
        invoice.save()
        wallet = self.wallet_object()
        wallet.invoices.add(invoice)
        wallet.save()
        return invoice


    ## We don't have these fields in the model just yet
    # def create_stripe_address(self):
    # 	address={
    # 		"line1":self.up.address,
    # 		"city":self.up.town,
    # 		"state":self.up.county,
    # 		"postal_code": self.up.post_code,
    # 		"country": self.up.country_alpha_2
    # 		}
    # 	return address

    def post_profile(self):
        stripe_customer = stripe.Customer.create(
            email = self.user.email, 
            # name = self.up.full_name(),
            # address = self.create_stripe_address()
            )
        wallet = self.wallet_object()
        wallet.stripe_id = stripe_customer["id"]
        wallet.save()
        return stripe_customer

    def put_profile(self):
        stripe_customer = stripe.Customer.modify(
            self.stripe_id(),
            email = self.up.email(), 
            name = self.up.full_name(),
            # address = self.create_stripe_address()
            )
        return stripe_customer

    def get_profile(self):
        stripe_customer = stripe.Customer.retrieve(
            self.stripe_id(),
            )
        return stripe_customer

    def list_sources(self):
        try:
            sources = stripe.Customer.list_sources(self.stripe_id(),limit=3,object='card')
        except TypeError:
            sources = []
        return sources

    def get_source(self):
        source = stripe.Customer.retrieve_source(self.stripe_id(),self.source_id)
        return source

    def put_source(self, source_id):
        source = stripe.Customer.retrieve_source(self.stripe_id(),source_id)
        put_source = stripe.Customer.modify(
                    self.stripe_id(), 
                    default_source=source["id"],
                    )
        source_obj = self.source_object(source["id"])
        source_obj.is_default = True
        source_obj.save()
        return put_source

    def post_source(self):
        stripe_id = self.stripe_id()
        source = stripe.Customer.create_source(
            stripe_id,
            source=self.token
            )
        self.put_source(source["id"])
        return source

    def get_invoice_item(self):
        invoice_item = stripe.InvoiceItem.retrieve(self.invoice_item_id)
        return invoice_item

    def put_invoice_item(self):
        invoice_item = stripe.InvoiceItem.modify(self.invoice_item_id)
        return invoice_item

    def post_invoice_item(self, item):
        quantity = int(item.quantity)
        amount = int(item.amount())
        unit_amount = int(amount / quantity)
        line = stripe.InvoiceItem.create(
            customer= self.stripe_id(),
            unit_amount= unit_amount,
            quantity = int(item.quantity),
            currency=self.currency.lower(),
            description= item.item.content_object.title
            )
        line = self.line_object(line["id"], item)

        invoice_item = stripe.InvoiceItem.create(
                customer= self.stripe_id(),
                unit_amount= unit_amount,
                quantity = int(item.quantity),
                currency=self.currency.lower(),
                description= self.description
            )
        return line

    def list_invoices(self):
        invoices = stripe.Invoice.list(self.stripe_id())
        return invoices

    def get_source_data(self):

        source_data = {"sources":{},"has_sources":False}
        try:
            sources = self.list_sources()
            customer = self.get_profile()
            default_source = customer["default_source"]
            source_obj = self.source_object(default_source)
            source_obj.is_default = True
            source_obj.save()
            exclude_id = [source_obj.id]
            #manage default
            user_sources = self.wallet_object().sources.exclude(id__in=exclude_id)
            for source in user_sources:
                source.is_default = False
                source.save()
            source_list = []
            for source in sources["data"]:
                source_info = {"id": "", "stripe_id": "", "type": "", "card": "", "exp": "", "default": ""}
                date = datetime.strptime(f'{source["exp_month"]}/{source["exp_year"]}', '%m/%Y')
                date2 = date + relativedelta(months=+1)
                exp_date = date2 + relativedelta(days=-1)
                today = date.today()

                source_obj = self.source_object(source["id"])
                if today <= exp_date:
                    source_info["id"] = source_obj.id
                    source_info["stripe_id"] = source["id"]
                    source_info["type"] = source["brand"]
                    source_info["default"] = source_obj.is_default
                    source_info["card"] = f'**** {source["last4"]}'

                    if source["exp_month"] < 9:
                        mnt = f'0{source["exp_month"]}'
                    else:
                        mnt = source["exp_month"]

                    year = source["exp_year"] - 2000
                    source_info["exp"] = f'{mnt}/{year}'
                    
                source_list.append(source_info)
            source_data["has_sources"] = True
            source_data["sources"] = source_list
        except:
            return source_data
        return source_data
        
    def get_invoice_data(self):

        invoice_data = {"invoices":{},"has_invoices":False}
        try:
            invoices = self.list_invoices()
            invoice_list = []
            for invoice in invoices["data"]:
                invoice_info = {
                    "invoice_id": invoice["id"], 
                    "invoice_url": invoice["hosted_invoice_url"], 
                    "invoice_pdf": invoice["invoice_pdf"], 
                    "invoice_description": invoice["lines"]["data"][0]["description"],
                    "invoice_total": invoice["amount_paid"]/100,
                    "invoice_paid": invoice["paid"],
                    "invoice_date": datetime.fromtimestamp(int(invoice["created"])).strftime('%d-%m-%Y'),
                    }

                invoice_list.append(invoice_info)
            invoice_data["has_invoices"] = True
            invoice_data["invoices"] = invoice_list

        except:
            return invoice_data
        return invoice_data

    def get_invoice(self):
        invoice = stripe.Invoice.retrieve(self.invoice_id)
        invoice_info = {
                    "invoice_id": invoice["id"], 
                    "invoice_url": invoice["hosted_invoice_url"], 
                    "invoice_pdf": invoice["invoice_pdf"], 
                    "invoice_description": invoice["lines"]["data"][0]["description"],
                    "invoice_total": invoice["amount_paid"]/100,
                    "invoice_paid": invoice["paid"],
                    "invoice_date": datetime.fromtimestamp(int(invoice["created"])).strftime('%d-%m-%Y'),
                    }
        return invoice_info

    def post_invoice(self):

        cart = self.cart
        amount = cart.amount

        if self.token:
            source = self.post_source()
            self.source_id = source["id"]
        
        #create invoice items
        items = []
        for item in cart.items.all():
            items.append(self.post_invoice_item(item))
        
        #created invoice items will automatically be added to this invoice
        new_invoice = stripe.Invoice.create(
            customer=self.stripe_id(),
            #Worry about this later
            #default_tax_rates=[self.tax_id],
            collection_method="charge_automatically",
        )

        #manually finalize the invoice before making a payment request
        invoice = stripe.Invoice.finalize_invoice(new_invoice.id)

        try:
            #pay the invoice
            stripe.Invoice.pay(
                invoice.id,
                source=self.source_id,
                )

            invoice = self.invoice_object(invoice.id, items, self.source_id)

            
        except stripe.error.CardError as e:
            message = "Card Error"
            status = "500"
            return {"status": status, "message": message}

        except stripe.error.RateLimitError as e:
            message = "Rate limit error"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.InvalidRequestError as e:
            message = "Invalid parameter"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.AuthenticationError as e:
            message = "Not authenticated"
            status = "500"
            return {"status": status, "message": message}

        except stripe.error.APIConnectionError as e:
            message = "Network error"
            status = "500"
            return {"status": status, "message": message}
        
        except stripe.error.StripeError as e:
            message = "Something went wrong, you were not charged"
            status = "500"
            return {"status": status, "message": message}
        
        except Exception as e:
            message = "Serious error, we have been notified"
            status = "500"
            return {"status": status, "message": message}

        #clear carts
        CartItem.objects.clear_items(self.user)
        
        #send data to API
        self.send_to_api(invoice)

        message = "Success! Your payment was successful"
        status = "200"
        return {"status": status, "message": message, "id":invoice.id}

    def send_to_api(self, invoice):
        headers = {
            'Content-Type': 'application/vnd.api+json',
        }
        url = f'{settings.API_URL}/assets/'
        for line in invoice.lines.all():
            data = create_api_json(
                str(line.id),
                "6dd2b6d8-0c26-11ed-861d-0242ac120002",
                float(line.sell_amount.amount),
                line.sell_amount_currency,
                line.quantity,
                str(line.user.id),
                float(line.buy_amount.amount),
                line.buy_amount_currency,
                'http://localhost:7070/media/seller%40didcoding.com/products/tokens/Token%20to%20sell/hbar.png',
                'http://localhost:7070/media/seller%40didcoding.com/products/tokens/Token%20to%20sell/hbar.png',
                "6dd2b6d8-0c26-11ed-861d-0242ac120002")

            api = APIRequestor(
                url = url,
                headers = headers,
                data = json.dumps(data, indent = 4),
            )
            #post data
            resp = api.post()
            line.asset_id = resp.json()["data"]["id"]
            line.save()


    def print_webhook_event(obj, action):
    try:
        if len(obj)>0:
            obj = obj[0]
    except TypeError:
        pass
    obj_content_type = ContentType.objects.get_for_model(obj)
    print_text = f"⚠️ Webhook event ⚠️ - obj:{obj_content_type.app_label}.{obj_content_type.model}, action:{action}"
    return print_text

    def convert_naive_to_aware(date):
    return date


    class CustomerHandler:
    def __init__(self, data, method):
        self.method = method
        self.data = data
        self.stripe_id = self.data["id"]

    def get(self):
        try:
            wallet = Wallet.objects.get(stripe_id=self.stripe_id)
        except Wallet.DoesNotExist:
            print('Wallet not found')
            wallet = None
        return wallet

    def deleted(self):
        obj = self.get()
        if obj:
            obj.stripe_id = ""
            obj.save()
            print(print_webhook_event(obj, 'deleted'))

    def updated(self):
        wallet = self.get()
        if wallet:
            obj = wallet.user.userprofile
            
            #change country alpha_2 to name
            # country =  self.data["address"]["country"]
            # country_name = pycountry.countries.get(alpha_2 = country).name
            ## We need to add this to userprofiles
            # obj.country = country_name
            # obj.address = self.data["address"]["line1"]
            # obj.town = self.data["address"]["city"]
            # obj.county = self.data["address"]["state"]
            # obj.post_code = self.data["address"]["postal_code"]
            obj.save()
            print(print_webhook_event(obj, 'updated'))

    def created(self):
        obj = self.get()
        #Do we really want to create customers in Stripe??
        print(print_webhook_event(obj, 'created'))

