"""
IP Calculator app
"""

from flask import Flask, url_for, render_template, request, redirect
from random import randint, shuffle
import logging
import numpy

#another necessary comment huehue
logging.basicConfig(format="%(asctime)s - %(message)s", level=logging.INFO)
logger = logging.getLogger('root')
app = Flask(__name__)
app.config['SECRET_KEY'] = 'gshfkjgh1kj2hkj4hkj'
dogs = ['dog-1.jpg', 'dog-2.jpg', 'dog-3.jpg', 'dog-4.jpg']


def dec_to_bin(decimal):
    mylist = []
    while decimal != 1:
        if decimal == 0:
            break
        elif decimal % 2 == 0:
            mylist.append(str(0))
            decimal = decimal // 2
        elif decimal % 2 == 1:
            mylist.append(str(1))
            decimal = decimal // 2
    if decimal == 0:
        mylist.append(str(0))
    else:
        mylist.append(str(1))
    return ''.join(mylist[::-1])

def bin_to_dec(binary):
    mylist = list(enumerate(binary))
    dec = int()
    indexes = []
    values = []
    for index, value in mylist:
        indexes.append(index)
        values.append(value)
    indexes = indexes[::-1]
    zipped = zip(indexes, values)
    for index, value in zipped:
        if int(value) != 0:
            dec += (2 * int(value)) ** index
    return dec


def turn_ip_to_bin(ip):
    ip_splitted = ip.split('.')
    binary_ip_list = [dec_to_bin(int(octet)) for octet in ip_splitted]
    for octet in binary_ip_list:
        if len(octet) != 8:
            count = 8 - len(octet)
            new = count * "0" + octet
            binary_ip_list[binary_ip_list.index(octet)] = new
    return '.'.join(binary_ip_list)


def rtrv_ip_mask(ip):
    values = tuple(ip.split("/"))
    return values


def divide_to_octets(zero_one_address):
    mask_helper = []
    counter = 0
    helper = False
    for i in zero_one_address:
        if counter % 8 != 0 or counter == 0:
            if helper:
                mask_helper.append(helper)
                counter += 1
            helper = False
            mask_helper.append(f'{i}')
            counter += 1
        else:
            mask_helper.append('.')
            helper = i
            counter = 0
    bin_mask = ''.join(mask_helper)
    return bin_mask


def insert_separator_line(bin_address, mask_num):
    bin_address_splitted = bin_address.split('.')
    if mask_num <= 8:
        bin_address_splitted[0] = bin_address_splitted[0][0:mask_num] + ' | ' + bin_address_splitted[0][mask_num:]
    elif 8 < mask_num <= 16:
        mask_num = (mask_num % 8) if mask_num != 16 else 8
        bin_address_splitted[1] = bin_address_splitted[1][0:mask_num] + " | " + bin_address_splitted[1][mask_num:]
    elif 16 < mask_num <= 24:
        mask_num = (mask_num % 8) if mask_num != 24 else 8
        bin_address_splitted[2] = bin_address_splitted[2][0:mask_num] + " | " + bin_address_splitted[2][mask_num:]
    else:
        mask_num = (mask_num % 8) if mask_num != 32 else 8
        bin_address_splitted[3] = bin_address_splitted[3][0:mask_num] + " | " + bin_address_splitted[3][mask_num:]
    return '.'.join(bin_address_splitted)


def calculate_subnet_broadcast_and_hosts(address):
    ip, mask_num = rtrv_ip_mask(address)
    mask_zero_one = int(mask_num) * '1' + (32 - int(mask_num)) * '0'
    bin_mask = divide_to_octets(mask_zero_one)
    bin_ip = turn_ip_to_bin(ip)
    host_number = 2 ** (32 - int(mask_num)) - 2
    bin_ip_list = bin_ip.split('.')
    bin_mask_list = bin_mask.split('.')
    ip_mask_zipped = list(zip(bin_ip_list, bin_mask_list))
    subnet = []
    for ip_octet, mask_octet in ip_mask_zipped:
        ip_octet_list = numpy.array([int(element) for element in ip_octet])
        mask_octet_list = numpy.array([int(element) for element in mask_octet])
        logic_and = list(ip_octet_list & mask_octet_list)
        logic_and_str = [str(element) for element in logic_and]
        subnet.append(''.join(logic_and_str))
    broadcast, bin_broadcast = calculate_broadcast('.'.join(subnet), mask_num)
    subnet_dec = [str(bin_to_dec(element)) for element in subnet]
    mask_dec = [str(bin_to_dec(element)) for element in bin_mask_list]
    bin_mask = insert_separator_line(bin_mask, int(mask_num))
    bin_subnet = insert_separator_line('.'.join(subnet), int(mask_num))
    bin_broadcast = insert_separator_line('.'.join(bin_broadcast), int(mask_num))
    bin_ip = insert_separator_line(bin_ip, int(mask_num))
    return '.'.join(subnet_dec), '.'.join(mask_dec), broadcast, host_number, bin_subnet, bin_mask, bin_ip, bin_broadcast, mask_num


def calculate_broadcast(subnet_ip, mask_num):
    subnet_list = [element for element in subnet_ip if element != '.']
    broadcast_list = []
    for index, value in enumerate(subnet_list):
        if index < int(mask_num):
            broadcast_list.append(value)
        else:
            broadcast_list.append('1')
    broadcast_address_binary = divide_to_octets(''.join(broadcast_list)).split('.')
    broadcast_address_dec = '.'.join([str(bin_to_dec(element)) for element in broadcast_address_binary ])
    return broadcast_address_dec, broadcast_address_binary


def random_ip_address():
    mask_num = "/" + str(randint(1, 32))
    ip_address_list = [str(randint(1, 255)), str(randint(0, 255)), str(randint(0, 255)), str(randint(0, 255))]
    ip_address = '.'.join(ip_address_list) + mask_num
    return ip_address


@app.route("/", methods=['POST', 'GET'])
def index(template_name="ipcalc.html"):
    shuffle(dogs)
    randomip = random_ip_address()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Random':
            shuffle(dogs)
            return render_template(f"{template_name}", randomip=randomip, dogs=dogs, templatename=template_name)
        elif request.form['submit_button'] == 'Calculate':
            shuffle(dogs)
            ipaddress = request.form['ipaddress']
            subnet, mask, broadcast, hosts, bin_subnet, bin_mask, bin_ip, bin_broadcast, mask_num = \
                calculate_subnet_broadcast_and_hosts(str(ipaddress))
            return render_template(f"{template_name}", ipaddress=ipaddress, subnet=subnet, mask=mask, broadcast=broadcast,
                                   hosts=hosts, dogs=dogs, binsubnet=bin_subnet, binmask=bin_mask,
                                   binip=bin_ip, binbroadcast=bin_broadcast, masknum=mask_num, templatename=template_name)
    return render_template(f"{template_name}", dogs=dogs, templatename=template_name)

@app.route("/learning", methods=["POST", "GET"])
def learning(template_name="learning.html"):
    shuffle(dogs)
    randomip = random_ip_address()
    if request.method == 'POST':
        if request.form['submit_button'] == 'Random':
            shuffle(dogs)
            return render_template(f"{template_name}", randomip=randomip, dogs=dogs, templatename=template_name)
        elif request.form['submit_button'] == 'Calculate':
            shuffle(dogs)
            ipaddress = request.form['ipaddress']
            subnet, mask, broadcast, hosts, bin_subnet, bin_mask, bin_ip, bin_broadcast, mask_num = \
                calculate_subnet_broadcast_and_hosts(str(ipaddress))
            calculated = {"subnet": subnet, "mask": mask, "broadcast": broadcast, "hosts": str(hosts)}
            inserted_values = {"subnet": request.form['subnetcheck'], "mask": request.form['maskcheck'],
                               "broadcast": request.form['broadcheck'], "hosts": request.form['hostcheck']}
            subnet_verification = "OK" if inserted_values["subnet"] == calculated["subnet"] else "NOK"
            mask_verification = "OK" if inserted_values['mask'] == calculated["mask"] else "NOK"
            broadcast_verification = "OK" if inserted_values["broadcast"] == calculated["broadcast"] else "NOK"
            host_verification = "OK" if inserted_values["hosts"] == calculated["hosts"] else "NOK"
            return render_template(f"{template_name}", ipaddress=ipaddress, subnet=subnet, mask=mask,
                                   broadcast=broadcast,
                                   hosts=hosts, dogs=dogs, binsubnet=bin_subnet, binmask=bin_mask,
                                   binip=bin_ip, binbroadcast=bin_broadcast, masknum=mask_num,
                                   subnetverification=subnet_verification, maskverification=mask_verification,
                                   broadcastverification=broadcast_verification, hostverification=host_verification,
                                   inserted=inserted_values, templatename=template_name)
    return render_template(f"{template_name}", dogs=dogs, templatename=template_name)

#this is test comment, working in branch hehe
if __name__ == "__main__":
    app.run(debug=True)