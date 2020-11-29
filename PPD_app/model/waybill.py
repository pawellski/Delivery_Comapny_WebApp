from fpdf import FPDF
import os

class Waybill:

    def __init__(self, id: str, sender, recipient):
        self.__id = id
        self.__sender = sender
        self.__recipient = recipient
    
    def generate_and_save(self, path="./"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        self.__add_table_to_pdf(pdf)
        
        filename = self.__create_filename(path)
        pdf.output(filename)

        return filename

    def __add_table_to_pdf(self, pdf):
        n_cols = 2
        col_width = (pdf.w - pdf.l_margin - pdf.r_margin) / n_cols
        font_size = pdf.font_size
        n_lines = 5

        pdf.cell(col_width, n_lines * font_size, "Nadawca", border=1)
        pdf.multi_cell(col_width, font_size, txt=self.__sender.str_full(), border=1)
        pdf.ln(0)
        pdf.cell(col_width, n_lines * font_size, "Adresat", border=1)
        pdf.multi_cell(col_width, font_size, txt=self.__recipient.str_full(), border=1)
        image_name = "waybill_images/" + self.__id + ".png"
        if os.path.isfile(image_name):
            x = (pdf.w / 2) - 50
            pdf.image(image_name, x, y = 75, w = 100, h = 100)

    def __create_filename(self, path):
        return "{}{}.pdf".format(path, self.__id)


    
class Person:

    def __init__(self, name: str, surname: str, address, phone_number: str):
        self.__name = name
        self.__surname = surname
        self.__address = address
        self.__phone_number = phone_number

    def get_fullname(self):
        return "{} {}".format(self.__name, self.__surname)
    
    def get_address(self):
        return self.__address.str_full()

    def get_phone_number(self):
        return self.__phone_number
    
    def str_full(self):
        return "{}\n{}\n{}".format(self.get_fullname(), self.get_address(), self.get_phone_number())


class Address:

    def __init__(self, street: str, number: str, postal_code: str, city: str, country: str):
        self.__street = street
        self.__number = number
        self.__postal_code = postal_code
        self.__city = city
        self.__country = country

    def get_street_and_number(self):
        return "{} {}".format(self.__street, self.__number)
    
    def get_postal_code_and_city(self):
        return "{} {}".format(self.__postal_code, self.__city)

    def get_country(self):
        return self.__country

    def str_full(self):
        return "{}\n{}\n{}".format(self.get_street_and_number(),
            self.get_postal_code_and_city(), self.get_country())