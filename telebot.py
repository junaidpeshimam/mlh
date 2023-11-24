import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Initialize the bot and your API token
bot = telebot.TeleBot("6291751300:AAHQVSG0I2D0ZfCFZ_MOyJO8B7QeQBmBXi4")

# Create a dictionary to keep track of the user's state
user_data = {}

# Replace 'YOUR_PERSONAL_CHAT_ID' with your personal chat ID
PERSONAL_CHAT_ID = '1226327771'
PERSONAL_CHAT_ID2 = '5525236059'



@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Initialize user data dictionary

    bot.send_message(chat_id, "Hey, welcome to India's first Fuel Delivery Service Bot! We deliver Fuel at your doorstep.")
    bot.send_message(chat_id, "You can Always use the Menu 三 Tab to Place and Cancel Orders Anytime")
    bot.send_message(chat_id, "How can we help you today?\nWhat would you like to choose?", reply_markup=generate_fuel_options())

def generate_fuel_options():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Order Petrol", callback_data="order_petrol"))
    markup.add(InlineKeyboardButton("Order Diesel", callback_data="order_diesel"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data in ["order_petrol", "order_diesel"])
def handle_fuel_order(call):
    chat_id = call.message.chat.id
    fuel_type = call.data.replace("order_", "")
    user_data[chat_id]['fuel_type'] = fuel_type

    bot.send_message(chat_id, f"Please Note that: \nPetrol = ₹112 \nDiesel = ₹99")
    bot.send_message(chat_id, f"How many Litres of {fuel_type} do you want to order?", reply_markup=generate_liter_options())

def generate_liter_options():
    markup = InlineKeyboardMarkup(row_width=3)

    for i in range(1, 6):
        markup.add(InlineKeyboardButton(f"{i} Litre ", callback_data=f"liters_{i}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith("liters_"))
def store_liter(call):
    chat_id = call.message.chat.id
    liters = int(call.data.split("_")[1])
    user_data[chat_id]['liters'] = liters

    bot.send_message(chat_id, "Please provide the following details:")
    bot.send_message(chat_id, "Name:")
    bot.register_next_step_handler(call.message, get_name)

def get_name(message):
    chat_id = message.chat.id
    name = message.text
    user_data[chat_id]['name'] = name

    bot.send_message(chat_id, "Phone No:")
    bot.register_next_step_handler(message, get_phone)

def get_phone(message):
    chat_id = message.chat.id

    while True:
        phone = message.text

        if len(phone) == 10:
            user_data[chat_id]['phone'] = phone
            break  # Break out of the loop if a valid phone number is provided
        else:
            bot.send_message(chat_id, "Invalid phone number. Please enter a valid 10-digit phone number.")
            bot.send_message(chat_id, "Phone No:")
            bot.register_next_step_handler(message, get_phone)
            return  # Return to avoid proceeding to the next step in the meantime

    # Continue with the rest of your code...
    bot.send_message(chat_id, "Address:")
    bot.register_next_step_handler(message, get_address)


def get_address(message):
    chat_id = message.chat.id
    address = message.text
    user_data[chat_id]['address1'] = address

    bot.send_message(chat_id, "Please send your live location to confirm the address.")
    bot.send_message(chat_id, "You can do this by using the 'Share My Location' feature and then sending the generated link.")
    bot.send_message(chat_id, "Click the Clip Pin 🧷 and choose location to share current location")
from telebot import types

@bot.message_handler(content_types=['location'])
def receive_location(message):
    chat_id = message.chat.id

    if chat_id in user_data:
        user_data[chat_id]['location'] = message.location
        latitude = user_data[chat_id]['location'].latitude
        longitude = user_data[chat_id]['location'].longitude

        # Create a link using the latitude and longitude
        location_link = f"https://maps.google.com/?q={latitude},{longitude}"

        bot.send_message(chat_id, "Your location has been updated. Here is a live location link:")
        bot.send_message(chat_id, location_link)  # Send the live location link to the user

        # Send the live location link to your personal chat ID
        # send_live_location_to_personal_account(chat_id, location_link)

        bot.send_message(chat_id, "Do you want to proceed with this location?", reply_markup=generate_confirm_edit_buttons())

# def send_live_location_to_personal_account(chat_id, location_link):
#     if chat_id in user_data:
#         order_data = user_data[chat_id]
#         confirmation_message = f"New Order:\nName: {order_data['name']}\nPhone: {order_data['phone']}\nLitres: {order_data['liters']} {order_data['fuel_type']}\nLocation: {location_link}"
#         bot.send_message(PERSONAL_CHAT_ID, confirmation_message)

def generate_confirm_edit_buttons():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(InlineKeyboardButton("Confirm", callback_data="confirm"))
    markup.add(InlineKeyboardButton("Edit", callback_data="edit"))
    return markup

@bot.message_handler(commands=['order'])
def start_order(message):
    chat_id = message.chat.id
    user_data[chat_id] = {}  # Initialize user data dictionary for the new order

    bot.send_message(chat_id, "You have started a new order. How can we help you today?")
    bot.send_message(chat_id, "What would you like to choose?", reply_markup=generate_fuel_options())

@bot.message_handler(commands=['cancel'])
def cancel_order(message):
    chat_id = message.chat.id

    if chat_id in user_data:
        order_data = user_data[chat_id]
        if 'location' in order_data:
            bot.send_message(chat_id, "Your current order has been canceled.")
            send_cancellation_to_personal_account(chat_id, order_data)
            user_data.pop(chat_id)  # Clear the user's data

        else:
            bot.send_message(chat_id, "There is no active order to cancel.")
            bot.send_message(chat_id,"Please Place a new order with /order")
    else:
        bot.send_message(chat_id, "There is no active order to cancel.")
        bot.send_message(chat_id,"Please Place a new order with /order")

def send_cancellation_to_personal_account(chat_id, order_data):
    location_link = f"https://maps.google.com/?q={order_data['location'].latitude},{order_data['location'].longitude}"
    cancellation_message = f"Order Canceled:\nName: {order_data['name']}\nPhone: {order_data['phone']}\nLitres: {order_data['liters']} {order_data['fuel_type']}\nAddress: {order_data['address1']}\nLocation: {location_link}"
    bot.send_message(PERSONAL_CHAT_ID, cancellation_message)
    bot.send_message(PERSONAL_CHAT_ID2, cancellation_message)


@bot.callback_query_handler(func=lambda call: call.data in ["confirm", "edit"])
def confirm_or_edit(call):
    chat_id = call.message.chat.id
    if call.data == "confirm":
        if chat_id in user_data:
            order_data = user_data[chat_id]

            # Generate the live location link
            location_link = f"https://maps.google.com/?q={order_data['location'].latitude},{order_data['location'].longitude}"

            # Send the confirmation message with the live location link
            send_confirmation_to_personal_account(chat_id, order_data, location_link)

            bot.send_message(chat_id, "Your order has been confirmed. Thank you!")
            bot.send_message(chat_id, "Thank you for using our service!")
    else:
        if chat_id in user_data:
            user_data.pop(chat_id)  # Clear the user's data
        bot.send_message(chat_id, "Your order has been edited. Let's start the process again.")
        send_welcome(call.message)

def send_confirmation_to_personal_account(chat_id, order_data, location_link):
    confirmation_message = f"New Order:\nName: {order_data['name']}\nPhone: {order_data['phone']}\nLitres: {order_data['liters']} {order_data['fuel_type']}\nAdress: {order_data['address1']}\nLocation: {location_link}"
    bot.send_message(PERSONAL_CHAT_ID, confirmation_message)
    bot.send_message(PERSONAL_CHAT_ID2, confirmation_message)


# Start polling for incoming messages
bot.polling()
