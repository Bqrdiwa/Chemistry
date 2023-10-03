from ippanel import Client

api_key = "inj29QmiusdNG2Meu0kbD2LHG9n18Fi1i5nUGkEYkWo="

# create client instance
sms = Client(api_key)

credit = sms.get_credit()
print(credit)

message_id = sms.send(
    "+983000505",          # originator
    ["989222945873",'989183394617'],    # recipients
    "ippanel is awesome",
     'to be logged' # message
)

print(message_id)