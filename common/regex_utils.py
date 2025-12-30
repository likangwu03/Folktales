import re

name_regex = r"^[A-Za-z]+([ A-Za-z]+)*"

snake_case_regex = r"^[a-z]+(_[a-z]+)*$"

relationship_regex = r"Therefore, their relationship is:\s*['\"]?([^'\"\s.]+)"

def split_camel_case(text: str):
	'''Inserta espacios entre las minúsculas y mayúsculas.
	
	Esto es útil para convertir CamelCase o cameClase en un formato convencional.
	
	Ejemplos:
		camelCase       ->	camel Case
		CamelCaseText   ->	Camel Case Text
		simpleXMLFile   ->	simple XML File
	'''
	
	# (?< = [a-z]) --> las posición debe estar después de una letra mínuscula
	# (?< = [a-z]) --> las posición debe estar antes de una letra mayúscula
	# Combinados, encuentra cada posición donde el carácter anterior es una minúsucla y el el siguiente es una mayúscula (...a|B...)
	return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)

def title_case_to_snake_case(text: str):
	"""
	Convierte strings separados por espacios en snake_case.

	Ejemplos:
        'Hello World'          -> 'hello_world'
        'User Profile Name'    -> 'user_profile_name'
        'Convert THIS TEXT'    -> 'convert_this_text'
        'Some MixedCASE TEXT'  -> 'some_mixedcase_text'
        'Multiple   Spaces'    -> 'multiple_spaces'
		'   Leading and trailing spaces   ' -> 'leading_and_trailing_spaces'
	"""
	
	return text.lower().replace(" ", "_")

def snake_case_to_title_case(text: str):
	"""
    Convierte un string snake_case en Title Case.

    Ejemplos:
        hello_world			->	Hello World
        user_profile_name	->	User Profile Name
    """
	
	words = text.split('_')
	return " ".join(word.capitalize() for word in words)

def snake_case_to_pascal_case(text: str):
	"""
	Convierte un string snake_case en PascalCase.

	Ejemplos:
		hello_world         -> HelloWorld
		user_profile_name   -> UserProfileName
		simple_xml_file     -> SimpleXmlFile
	"""

	words = text.split('_')
	return "".join(word.capitalize() for word in words)

def snake_case_to_camel_case(text: str):
    """
    Convierte un string snake_case en camelCase.

    Ejemplos:
        hello_world         -> helloWorld
        user_profile_name   -> userProfileName
        simple_xml_file     -> simpleXmlFile
    """
    
    words = text.split('_')
    return words[0].lower() + "".join(word.capitalize() for word in words[1:])