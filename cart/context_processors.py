from .cart import Cart

# Create context processor so our cart can work on all pages of all site
def cart(request):
    return{'cart': Cart(request)}    # Return the default data from our Cart