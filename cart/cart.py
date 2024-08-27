from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session
        self.request = request  # Get request
        cart = self.session.get('session_key')     # Get the current session_key if it exists
        if 'session_key' not in request.session:    # If the use is new, no session_key! create one!
            cart = self.session['session_key'] = {}
        self.cart = cart    #Make sure cart id available on all pages of site

    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)
        # logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        if self.request.user.is_authenticated:  #Deal with login user
            current_user = Profile.objects.filter(user__id=self.request.user.id)    # Get the current user profile
            carty = str(self.cart)  # Convert {'4':1, '2':5} to {"4":2, "2":5}
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))    # Save carty to the Profile Model / str is for sure :)
       

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)
        # logic
        if product_id in self.cart:
            pass
        else:
            # self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
        self.session.modified = True
        if self.request.user.is_authenticated:  #Deal with login user
            current_user = Profile.objects.filter(user__id=self.request.user.id)    # Get the current user profile
            carty = str(self.cart)  # Convert {'4':1, '2':5} to {"4":2, "2":5}
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))    # Save carty to the Profile Model / str is for sure :)

    def cart_total(self):
        product_ids = self.cart.keys() # get product id
        products = Product.objects.filter(id__in=product_ids) 
        quantities = self.cart
        total = 0   #start calculate
        for key,value in quantities.items():
            key = int(key)  #convert string into intiger for math
            for product in products:
                if product.id == key:
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total
        

    def __len__(self):
        return len(self.cart)

    def get_prods(self):
        product_ids = self.cart.keys()    # Get Ids from cart
        products = Product.objects.filter(id__in=product_ids)    # use ids to lookup products in datebase models
        return products   # return those looked up products

    def get_quants(self):
        quantities = self.cart
        return quantities
    
    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)
        ourcart = self.cart   # get cart
        ourcart[product_id] = product_qty   # update ductionary/cart
        self.session.modified = True
        
        if self.request.user.is_authenticated:  #Deal with login user
            current_user = Profile.objects.filter(user__id=self.request.user.id)    # Get the current user profile
            carty = str(self.cart)  # Convert {'4':1, '2':5} to {"4":2, "2":5}
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))    # Save carty to the Profile Model / str is for sure :)

        thing = self.cart
        return thing
    
    def delete(self, product):
        product_id = str(product)
        if product_id in self.cart: # delete from dictionary/cart
            del self.cart[product_id]
        
        self.session.modified = True

        if self.request.user.is_authenticated:  #Deal with login user
            current_user = Profile.objects.filter(user__id=self.request.user.id)    # Get the current user profile
            carty = str(self.cart)  # Convert {'4':1, '2':5} to {"4":2, "2":5}
            carty = carty.replace("\'", "\"")
            current_user.update(old_cart=str(carty))    # Save carty to the Profile Model / str is for sure :)
