# Django course
This is my Django course. I hope you like it.

> These notes follow on from steps/shop_part_two.md
***
***

## Prepare your local project
You will need to clone down a new module to follow along.
```
git checkout shop_part_3
git pull origin shop_part_3
```


## Steps/Commands

>Note: Please 'cd' into the root directory and fire up your virtual environment!

Okay lets start where we left off in the last module. We now have views and url's all wired up. We now need to think about templates and static files.

Lets get started.

1) Templates - We need to create new html files for each of the main ecommerce views that we have created. Go ahead and create a new directory in /templates and call it ecommerce.

Create a new html file in /templates/ecommerce and call it items.html. Use the following code.
```
{% extends 'base/base.html' %}
{% load static  %}


{% block content %}
<h1>Shop items</h1>
<div class="row card-column">
  {% for object in object_list %}
  <div class="column">
    <div class="card">
      <img src="{{object.image.url}}" alt="{{object.title}}" style="width:100%">
      <h2>{{object.title}}</h2>
      <p class="price">{{object.variable_price}}</p>
      <p>{{object.description}}</p>
      <p>  
        <form>
          <div class="form-group row">
            <label for="quantity" class="col-sm-4 col-form-label">Stock</label>
            <div class="col-sm-7">
              <input type="text" name="stock-{{object.id}}" id="stock-input-{{object.id}}" class="stock-input-{{object.id}}" readonly value="{{object.stock}}">
            </div>
            <div class="col-sm-1">
            </div>
          </div>
        </form>
      </p>
      <p><a class="btn btn-primary" href="{{object.get_absolute_url}}" >&#x2607;</a></p>
    </div>
  </div>
  {% endfor %}
</div>
{% endblock %}

```
Create a new html file in /templates/ecommerce and call it item.html. Use the following code.
```
{% extends 'base/base.html' %}
{% load static ecommerce_tags %}

{% block content %}

<h3>Item - {{object.title}}</h3>

<div class="container">
    <div class="row">
        <div class="col-6">
            <form>
                <label for="stock">Price per item</label>
                <input type="text" readonly value="{{object.variable_price}}">
                <label for="stock">Stock</label>
                <input type="text" name="stock-{{object.id}}" id="stock-input-{{object.id}}" class="stock-input-{{object.id}}" readonly value="{{object.stock}}">
                <label for="quantity">Quantity</label>
                <input type="number" min="1" name="quantity-{{object.id}}" id="quantity-input-{{object.id}}" class="quantity-input-{{object.id}}" value="0">
            </form>
        </div>
    <div class="col-6">
        <img src="{{object.image.url}}" alt="{{object.title}}" class="image">
    </div>
    
</div>
    {% item_button item %}
</div>
{% endblock %}
```
Create a new html file in /templates/ecommerce and call it cart.html. Use the following code.

```
{% extends 'base/base.html' %}
{% load static ecommerce_tags mathfilters %}

{% block content %}

<h1>Cart</h1>


<div class="row">
  <div class="col-75">
    {% for object in request.user.cart.items.all %}
    <div class="column item-list-{{object.item.id}}">
      <div class="card">
        
        <img src="{{object.item.image.url}}" alt="{{object.item.title}}" style="width:100%">
        <h2>{{object.item.title}}</h2>
        <p class="price">{{object.item.price}}</p>
        <p>{{object.item.description}}</p>
        <p>  
          <form>
            <div class="form-group row">
              <div class="col-sm-2">
              {% item_button_v2 object.item %}
              </div>
              <label for="quantity" class="col-sm-4 col-form-label">Quantity</label>
              <div class="col-sm-6">
                <input readonly class="form-control-plaintext" name="quantity-{{object.id}}" id="quantity-input-{{object.id}}" class="quantity-input-{{object.id}}" value="{{object.quantity}}">
              </div>
            </div>
            
          </form>
        </p>
        <p><a class="btn btn-primary" href="{{object.item.get_absolute_url}}" >&#x2607;</a></p>
      </div>
    </div>
    {% endfor %}
  </div>

  <div class="col-25">
    <div class="container">
      <h4>Summary
        <span class="price" style="color:black">
          <i class="fa fa-cart-shopping"></i>
          <b class="item-count">{{request.user.cart.item_count}}</b>
        </span>
      </h4>
      <hr>
      <p>Total <span class="price" style="color:black"><b class="item-total-price">£{{request.user.cart.amount|div:100}}</b></span></p>
      <p><a class="btn btn-success" href="{% url 'ecommerce:checkout' %}">Go to checkout</a></p>
    </div>
  </div>
</div>
{% endblock %}

```

Create a new html file in /templates/ecommerce and call it checkout.html. Use the following code.
```
{% extends 'base/base.html' %}
{% load static ecommerce_tags mathfilters djmoney %}

{% block extend_head %}
<link rel="stylesheet" href="{% static 'stripe.css' %}">
{% endblock %}

{% block extend_foot %}
<script src="https://js.stripe.com/v3/"></script>
<script src="https://polyfill.io/v3/polyfill.min.js?version=3.52.1&features=fetch"></script>
<script src="{% static 'stripe.js' %}" defer></script>
<script type="text/javascript">
    var stripe_key = '{{stripe_key|safe}}'
</script>
{% endblock %}

{% block content %}

<h1>Checkout</h1>

<div class="row">
    <div class="col-75">
      <div class="container">
        {% if sources.has_sources %}
        <h4>Select a card to use</h4>
        <table id="saved-cards">
            <thead>
            <tr>

                <th>Type</th>
                <th>Card Number</th>
                <th>Exp date</th>
                <th>Is default</th>
                <th>Action</th>
            </tr>
            </thead>
            <tbody>
            {% for s in sources.sources %}
            <tr>

                <td>{{s.type}}</td>
                <td>{{s.card}}</td>
                <td>{{s.exp}}</td>
                <td>{{s.default}}</td>
                <td>{% if not s.default %}<a class="btn btn-warning source" value="{{s.stripe_id}}" >Make default</a>{% endif %}</td>
            </tr>
            {% endfor %}
            </tbody>
        </table>

        <br>
        <a class="btn btn-warning pay" value="{{default_card.stripe_id}}" >Pay <i class="item-total-price">{% money_localize request.user.cart.amount|div:100 request.user.wallet.currency %}</i> with default card</a>
        <br>

        {% endif %}
        <br>
        <h4>Pay with new card</h4>
        <form id="payment-form" style="width: 100%">
            {% csrf_token %}
            <div id="card-element"><!--Stripe.js injects the Card Element--></div>
            <button id="submit" type="submit">
            Pay <i class="item-total-price">£{{request.user.cart.amount|div:100}}</i> with new card
            </button>
            <p id="card-error" role="alert"></p>
            <p class="result-message hidden">
            Payment succeeded, see the result in your
            <a href="" target="_blank">Stripe dashboard.</a> Refresh the page to pay again.
            </p>
        </form>
      </div>
    </div>
  
    <div class="col-25">
      <div class="container">
        <h4>Cart
          <span class="price" style="color:black">
            <i class="fa fa-cart-shopping"></i>
            <b class="item-count">{{request.user.cart.item_count}}</b>
          </span>
        </h4>
        {% for object in request.user.cart.items.all %}
        <p class="item-list-{{object.item.id}}">{% item_button_v2 object.item %}
            <a href="{{object.item.content_object.get_absolute_url}}">{{object.item.content_object.title}}</a> <span class="price">£{{object.amount|div:100}}</span></p>
        {% endfor %}
        <hr>
        <p>Total <span class="price" style="color:black"><b class="item-total-price">£{{ request.user.cart.amount|div:100 }}</b></span></p>
      </div>
    </div>
  </div>



{% endblock %}

```
Create a new html file in /templates/ecommerce and call it item_button.html. Use the following code.

```
{% load static %}

{% comment %} this adds a plus to allow users to add items to cart!! {% endcomment %}
<a class="item btn btn-success" model="{{ target_model }}" id="target_{{ object_id }}" action="add">
	<i class="item-{{object_id}} fa-solid fa-cart-plus"></i>
	<span class="item-count-{{ object_id }}"></span>
</a>
```

Create a new html file in /templates/ecommerce and call it item_button_v2.html. Use the following code.

```
{% load static %}

{% comment %} this adds a plus to allow users to remove items from cart!! {% endcomment %}
<a style="color:red;" class="item" model="{{ target_model }}" id="target_{{ object_id }}" action="remove"><i class="item-{{object_id}} fa-solid fa-close"></i></a>
```

2) Template Tags - We are referencing template tags in our new templates so we'll need to create these. Create a new directory in /ecommerce called templatetags.
Now create a new file called __init__.py and another called ecommerce_tags.py. copy the following code and add it to /ecommerce/templatetags/ecommerce_tags.py.

```
from django import template
from django.template.loader import render_to_string
from ..models import Item
from ..utils import StripeManager
register = template.Library()


@register.simple_tag(takes_context=True)
def item_button(context, target):
    user = context['request'].user
    stripe_manager = StripeManager(user = user)

    # do nothing when user isn't authenticated
    if not user.is_authenticated:
        return ''

    target_model = '.'.join((target._meta.app_label, target._meta.object_name))
    undo = False
    cart = stripe_manager.cart_object()
    item_field = cart.items
    if cart.item_check(target):
        undo = True

    qty = cart.qty_check(target)

    return render_to_string(
        'ecommerce/item_button.html', {
            'target_model': target_model,
            'object_id': target.id,
            'object_quantity': qty,
            'object_stock': target.stock,
            'undo': undo,
            'item_count': item_field.all().count()
        }
    )

@register.simple_tag(takes_context=True)
def item_button_v2(context, target):
    user = context['request'].user
    stripe_manager = StripeManager(user = user)

    # do nothing when user isn't authenticated
    if not user.is_authenticated:
        return ''

    target_model = '.'.join((target._meta.app_label, target._meta.object_name))

    undo = False
    # prepare button to remove item if
    # already in cart

    cart = stripe_manager.cart_object()
    item_field = cart.items
    if cart.item_check(target):
        undo = True
    qty = cart.qty_check(target)
    return render_to_string(
        'ecommerce/item_button_v2.html', {
            'target_model': target_model,
            'object_id': target.id,
            'object_quantity': qty,
            'object_stock': target.stock,
            'undo': undo,
            'item_count': item_field.all().count()
        }
    )

```

3) Static files - Lastly, we need to create and import some JavaScript to tie all of our work together. 
Create a new html file in /static and call it main.js. Use the following code.

```
// Used to add a spinner to submit buttons
var temp_button_text;
function CustomFormSubmitPost(e) {
    var el = $(e);
    temp_button_text = el.text()
    el.attr('disabled', 'disabled').text("").append('<class="spinner-grow spinner-grow-sm" role="status" aria-hidden="true"></span>Loading...');
};
function CustomFormSubmitResponse(e) {
    var el = $(e);
    el.removeAttr('disabled').text(temp_button_text);
};


//ajax functions to alter tha like and bookmark buttons
"use strict";
var AJAXControls = function () {
    var item = function(){
        $('a.item').click(function() {
            var $obj = $(this);
            var target_id = $obj.attr('id').split('_')[1];
            var action = $obj.attr('action')
            var quantity = $('#quantity-input-'+target_id).val()
            $obj.prop('disabled', true);
            $.ajax({
                url: '/items/add-or-remove/',
                type: 'POST',
                data: {
                    target_model: $obj.attr('model'),
                    object_id: target_id,
                    object_quantity: quantity,
                    action: action
                },
                success: function(data) {
                    if (data["result"] == 'Success'){
                        $(".item-count").html(data["data"]["item_count"]);
                        $(".item-total-price").html(data["data"]["item_total_price"]);
                        $('#stock-input-'+target_id).val(data["data"]["stock"])
                        $('#quantity-input-'+target_id).val(0)
                        $obj.prop('disabled', false);
                        if (data["data"]["status"]=="remove"){
                            $(".item-list-" + target_id).remove();
                        }
                    }
                    ShowAlert(data["result"], data["message"], data["result"].toLowerCase(), data["redirect"]);
                }
            });
        });
    };

    var source = function(){
        $('a.source').click(function() {
            var $obj = $(this);
            var card_id = $obj.attr('value')
            $obj.prop('disabled', true);
            $.ajax({
                url: '/update-source/',
                type: 'POST',
                data: {
                    card_id: card_id,
                },
                success: function(data) {
                    ShowAlert(data["result"], data["message"], data["result"].toLowerCase(), data["redirect"]);
                }
            });
        });
    };

    var pay = function(){
        $('a.pay').click(function() {
            var $obj = $(this);
            var card_id = $obj.attr('value')
            $obj.prop('disabled', true);
            $.ajax({
                url: '/pay/',
                type: 'POST',
                data: {
                    card_id: card_id,
                },
                success: function(data) {
                    ShowAlert(data["result"], data["message"], data["result"].toLowerCase(), data["redirect"]);
                }
            });
        });
    };

    return {
        init: function () {
            item();
            source();
            pay();
        }
    };
}();

jQuery(document).ready(function () {
    AJAXControls.init();
});


$(function() {
    // This function gets cookie with a given name
    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie != '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) == (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    function sameOrigin(url) {
        // test that a given url is a same-origin URL
        // url could be relative or scheme relative or absolute
        var host = document.location.host; // host + port
        var protocol = document.location.protocol;
        var sr_origin = '//' + host;
        var origin = protocol + sr_origin;
        // Allow absolute or scheme relative URLs to same origin
        return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
            (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
            // or any other URL that isn't scheme relative or absolute i.e relative.
            !(/^(\/\/|http:|https:).*/.test(url));
    }
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                // Send the token to same-origin, relative URLs only.
                // Send the token only if the method warrants CSRF protection
                // Using the CSRFToken value acquired earlier
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
})

```
Create a new html file in /static and call it alert.js. Use the following code.

```
function ShowAlert(title, message, type, redirect) {
    if(redirect){
        toastr[type](message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            rtl: $("body").attr("dir") === "rtl" || $("html").attr("dir") === "rtl",
            timeOut: 1000,
            onHidden: function () {
                window.location.assign(redirect);
            }
        });
    }
    else{
        toastr[type](message, title, {
            positionClass: 'toast-bottom-right',
            closeButton: true,
            progressBar: true,
            newestOnTop: true,
            rtl: $("body").attr("dir") === "rtl" || $("html").attr("dir") === "rtl",
            timeOut: 1000,
        });
    }
};
```
Create a new html file in /static and call it stripe.js. Use the following code.

```
var stripe = Stripe(stripe_key);

// Create an instance of Elements.
var elements = stripe.elements();

// Custom styling can be passed to options when creating an Element.
// (Note that this demo uses a wider set of styles than the guide below.)
var style = {
base: {
  color: '#32325d',
  fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
  fontSmoothing: 'antialiased',
  fontSize: '16px',
  '::placeholder': {
    color: '#aab7c4'
  }
},
invalid: {
  color: '#fa755a',
  iconColor: '#fa755a'
}
};

// Create an instance of the card Element.
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');

// Handle real-time validation errors from the card Element.
card.addEventListener('change', function(event) {
    var displayError = document.getElementById('card-errors');
    if (event.error) {
    displayError.textContent = event.error.message;
    } else {
    displayError.textContent = '';
    }
});

// Create a token or display an error when the form is submitted.
var form = document.getElementById('payment-form');


form.addEventListener('submit', function(event) {
  event.preventDefault();
  stripe.createToken(card).then(function(result) {
    if (result.error) {
      
      // Inform the customer that there was an error.
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      // Send the token to your server.
      stripeTokenHandler(result.token);
    }
  });
});

function stripeTokenHandler(token) {
    // Insert the token ID into the form so it gets submitted to the server
    var form = document.getElementById('payment-form');
    var hiddenInput = document.createElement('input');
    hiddenInput.setAttribute('type', 'hidden');
    hiddenInput.setAttribute('name', 'stripeToken');
    hiddenInput.setAttribute('value', token.id);
    form.appendChild(hiddenInput);
    CustomFormSubmitPost($('#payment-form button[type=submit]'));
    $.ajax({
        method: "POST",
        url: "/pay/",
        data: {
          stripeToken: token.id,
        },
        success: function(data, textStatus, jqXHR){
          CustomFormSubmitResponse($('#payment-form button[type=submit]'));
          ShowAlert(data["result"], data["message"], data["result"].toLowerCase(), data["redirect"]);
        },
        error: function(xhr){
          console.log(xhr.status + ": " + xhr.responseText);
        }
    });
}
```
Create a new html file in /static and call it stripe.css. Use the following code.

```
/* Variables */
* {
    box-sizing: border-box;
  }
  
  #payment-form {
    width: 30vw;
    min-width: 500px;
    align-self: center;
    box-shadow: 0px 0px 0px 0.5px rgba(50, 50, 93, 0.1),
      0px 2px 5px 0px rgba(50, 50, 93, 0.1), 0px 1px 1.5px 0px rgba(0, 0, 0, 0.07);
    border-radius: 7px;
    padding: 40px;
  }
  
  #payment-form input {
    border-radius: 6px;
    margin-bottom: 6px;
    padding: 12px;
    border: 1px solid rgba(50, 50, 93, 0.1);
    height: 44px;
    font-size: 16px;
    width: 100%;
    background: white;
  }
  
  .result-message {
    line-height: 22px;
    font-size: 16px;
  }
  
  .result-message a {
    color: rgb(89, 111, 214);
    font-weight: 600;
    text-decoration: none;
  }
  
  .hidden {
    display: none;
  }
  
  #card-error {
    color: rgb(105, 115, 134);
    text-align: left;
    font-size: 13px;
    line-height: 17px;
    margin-top: 12px;
  }
  
  #card-element {
    border-radius: 4px 4px 0 0 ;
    padding: 12px;
    border: 1px solid rgba(50, 50, 93, 0.1);
    height: 44px;
    width: 100%;
    background: white;
  }
  
  #payment-request-button {
    margin-bottom: 32px;
  }
  
  /* Buttons and links */
  #payment-form button {
    background: #9c07b6;
    color: #ffffff;
    font-family: Arial, sans-serif;
    border-radius: 0 0 4px 4px;
    border: 0;
    padding: 12px 16px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    display: block;
    transition: all 0.2s ease;
    box-shadow: 0px 4px 5.5px 0px rgba(0, 0, 0, 0.07);
    width: 100%;
  }
  #payment-form button:hover {
    background-color: #730786;
  }
  #payment-form button:disabled {
    opacity: 0.5;
    cursor: default;
  }
  
  /* spinner/processing state, errors */
  .spinner,
  .spinner:before,
  .spinner:after {
    border-radius: 50%;
  }
  .spinner {
    color: #ffffff;
    font-size: 22px;
    text-indent: -99999px;
    margin: 0px auto;
    position: relative;
    width: 20px;
    height: 20px;
    box-shadow: inset 0 0 0 2px;
    -webkit-transform: translateZ(0);
    -ms-transform: translateZ(0);
    transform: translateZ(0);
  }
  .spinner:before,
  .spinner:after {
    position: absolute;
    content: "";
  }
  .spinner:before {
    width: 10.4px;
    height: 20.4px;
    background: #5469d4;
    border-radius: 20.4px 0 0 20.4px;
    top: -0.2px;
    left: -0.2px;
    -webkit-transform-origin: 10.4px 10.2px;
    transform-origin: 10.4px 10.2px;
    -webkit-animation: loading 2s infinite ease 1.5s;
    animation: loading 2s infinite ease 1.5s;
  }
  .spinner:after {
    width: 10.4px;
    height: 10.2px;
    background: #5469d4;
    border-radius: 0 10.2px 10.2px 0;
    top: -0.1px;
    left: 10.2px;
    -webkit-transform-origin: 0px 10.2px;
    transform-origin: 0px 10.2px;
    -webkit-animation: loading 2s infinite ease;
    animation: loading 2s infinite ease;
  }
  
  @-webkit-keyframes loading {
    0% {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }
    100% {
      -webkit-transform: rotate(360deg);
      transform: rotate(360deg);
    }
  }
  @keyframes loading {
    0% {
      -webkit-transform: rotate(0deg);
      transform: rotate(0deg);
    }
    100% {
      -webkit-transform: rotate(360deg);
      transform: rotate(360deg);
    }
  }
  
  @media only screen and (max-width: 600px) {
    form {
      width: 80vw;
    }
  }
```

Lastly, open templates/base/base.html and replace the code with the following.

```
<!DOCTYPE html>
{% load static %}
<html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">

    <!-- visit https://fonts.google.com/specimen/Courier+Prime?preview.text_type=custom to get script-->
    <link rel="preconnect" href="https://fonts.gstatic.com">
    <link href="https://fonts.googleapis.com/css2?family=Courier+Prime&display=swap" rel="stylesheet">

    <!--Bootstrap-->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">
    
    <!-- Toastr alerts -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.css" integrity="sha512-3pIirOrwegjM6erE5gPSwkUzO+3cTjpnV9lexlNZqvupR64iZBnOOTiiLPb9M36zpMScbmUNIcHUqKD47M719g==" crossorigin="anonymous" referrerpolicy="no-referrer" />
    
    <!--Fontawesome-->
    <script src="{% static 'fontawesomefree/js/all.min.js' %}"></script> 
    <script src="https://kit.fontawesome.com/8b7dd2a781.js" crossorigin="anonymous"></script>

    <!--Our own css-->
    <link rel="stylesheet" href="{% static 'main.css' %}">
    
    {% block extend_head %}<!-- This allows us to extend the head scripts in HTML docs that have special requirements-->{% endblock %}
    </head>
    <body>

    <!--Side nav-->
    {% if request.user.is_authenticated %}
    <ul class="sidenav">
        <li><a {% if 'account' in request.path %}class="active"{% endif %} href="{% url 'users:account' %}">User Account ({{request.user.username}})</a></li>
        <li><a {% if 'info' in request.path %}class="active"{% endif %}  href="{% url 'users:user-info' %}">User Info</a></li>
        <li><a href="{% url 'users:sign-out' %}">Sign Out</a></li>
        <li><a {% if 'item' in request.path %}class="active"{% endif %}  href="{% url 'ecommerce:items' %}">Shop Items</a></li>
        <li><a {% if 'cart' in request.path %}class="active"{% endif %}  href="{% url 'ecommerce:cart' %}">Cart</a></li>
    </ul>
    {% else %}
    <ul class="sidenav">
        <li><a {% if 'sign-in' in request.path %}class="active"{% endif %} href="{% url 'users:sign-in' %}">Sign in</a></li>
        <li><a {% if 'sign-up' in request.path %}class="active"{% endif %} href="{% url 'users:sign-up' %}">Sign up</a></li>
    </ul>
    {% endif %}

    <div class="div-container">
        {% block content %}<!--Used to add code to head-->{% endblock %}
    </div>

    <!--visit https://code.jquery.com/ for jquery script-->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>

    <!--Bootstrap-->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>

    <!-- Toastr -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/toastr.js/latest/toastr.min.js" integrity="sha512-VEd+nq25CkR676O+pLBnDW09R7VQX9Mdiij052gVCp5yVH3jGtH70Ho/UUv4mJDsEdTvqRCFZg0NKGiojGnUCw==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>

    <!--Our own j2-->
    <script src="{% static 'alert.js' %}"></script>
    <script src="{% static 'main.js' %}"></script>

    {% block extend_foot %}<!-- This allows us to extend the foot scripts in HTML docs that have special requirements-->{% endblock %}

    </body>
</html>
```

Now run the following code to round up all the new static files.
```
python manage.py collectstatic
```
You will now ba able to see the fruits of your labour at [http://localhost:8000](http://localhost:8000).
>Note: Open an incognito browser (Ctrl + Shift + N) as this will ensure your browser will grab the new changes.

***
***

## Root directory
>Note: If all went well, your root directory should now look like this
```
django_course\  <--This is the root directory
    core\
        __pycache__\
        migrations\
            __pycache__\
            >__init__.py
        >__init__.py
        >admin.py
        >apps.py
        >models.py
        >tests.py
        >urls.py
        >views.py
    ecommerce\
        __pycache__\
        migrations\
            __pycache__\
            >__init__.py
        >__init__.py
        >admin.py
        >apps.py
        >models.py
        >tests.py
        >urls.py
        >utils.py
        >views.py
    django_course\
        __pycache__\
        >__init__.py
        >asgi.py
        >settings.py
        >urls.py
        >wsgi.py
    media\
    mediafiles\ 
    static\
        >main.css
    staticfiles\
    steps\
        >account.md
        >admin.md
        >basics.md
        >basics_part_2.md
        >debug.md
        >env.md
        >shop_part_one.md
        >style.md
        >user_app_part_2.md
        >user_app.md
    templates\
        base\
            >base.html
        core\
            >index.html
        users\
            >account.html
            >info.html
            >sign_in.html
            >sign_up.html
    users\
        __pycache__\
        migrations\
            __pycache__\
            >__init__.py
            >0001_initial.py
        >__init__.py
        >admin.py
        >apps.py
        >forms.py
        >models.py
        >signals.py
        >tests.py
        >urls.py
        >views.py
    venv\
        include\
        Lib\
        Scripts\
    .env
    >.gitignore
    >db.sqlite3
    >manage.py
    >README.md
    >requirements.txt
```

***
***