from dataclasses import dataclass, field
from drafter import *
@dataclass
class ConversionRecord:
    value: float
    category: str
    from_unit: str
    to_unit: str
    result: float


@dataclass
class State:
    category: str = "Length"
    value: str = ""
    from_unit: str = "Meters"
    to_unit: str = "Centimeters"
    result: str = ""
    error_message: str = ""
    history: list[ConversionRecord] = field(default_factory=list)

# UNIT OPTIONS

def get_units(category: str) -> list[str]:
    if category == "Length":
        return ["Meters", "Centimeters", "Kilometers"]

    elif category == "Temperature":
        return ["Celsius", "Fahrenheit", "Kelvin"]

    elif category == "Electrical":
        return ["Volts", "Millivolts", "Amperes", "Milliamperes"]

    elif category == "Power":
        return ["Watts", "Kilowatts"]

    return []



# LENGTH CONVERSIONS


def convert_length(value: float, from_unit: str,
                   to_unit: str) -> float:

    # Convert the starting measurement into meters
    if from_unit == "Meters":
        meters = value
    elif from_unit == "Centimeters":
        meters = value / 100
    elif from_unit == "Kilometers":
        meters = value * 1000

    # Convert meters into the target unit
    if to_unit == "Meters":
        return meters
    elif to_unit == "Centimeters":
        return meters * 100
    elif to_unit == "Kilometers":
        return meters / 1000

    raise ValueError("Invalid length units")



# TEMPERATURE CONVERSIONS


def convert_temperature(value: float, from_unit: str, to_unit: str) -> float:

    # Converts the starting temperature into Celsius
    if from_unit == "Celsius":
        celsius = value

    elif from_unit == "Fahrenheit":
        celsius = (value - 32) * 5 / 9

    elif from_unit == "Kelvin":
        celsius = value - 273.15

    else:
        raise ValueError("Invalid starting temperature unit")

    # Converts Celsius into the target temperature
    if to_unit == "Celsius":
        return celsius

    elif to_unit == "Fahrenheit":
        return (celsius * 9 / 5) + 32

    elif to_unit == "Kelvin":
        return celsius + 273.15

    raise ValueError("Invalid target temperature unit")



# ELECTRICAL CONVERSIONS


def convert_electrical(value: float, from_unit: str, to_unit: str) -> float:

    # Voltage conversions
    if from_unit == "Volts" and to_unit == "Volts":
        return value

    elif from_unit == "Volts" and to_unit == "Millivolts":
        return value * 1000

    elif from_unit == "Millivolts" and to_unit == "Volts":
        return value / 1000

    elif from_unit == "Millivolts" and to_unit == "Millivolts":
        return value

    # Current conversions
    elif from_unit == "Amperes" and to_unit == "Amperes":
        return value

    elif from_unit == "Amperes" and to_unit == "Milliamperes":
        return value * 1000

    elif from_unit == "Milliamperes" and to_unit == "Amperes":
        return value / 1000

    elif from_unit == "Milliamperes" and to_unit == "Milliamperes":
        return value

    raise ValueError("You cannot convert voltage into current or current into voltage")



# POWER CONVERSIONS


def convert_power(value: float, from_unit: str,
                  to_unit: str) -> float:

    if from_unit == "Watts" and to_unit == "Watts":
        return value

    elif from_unit == "Watts" and to_unit == "Kilowatts":
        return value / 1000

    elif from_unit == "Kilowatts" and to_unit == "Watts":
        return value * 1000

    elif from_unit == "Kilowatts" and to_unit == "Kilowatts":
        return value

    raise ValueError("Invalid power units")



# MAIN CONVERSION FUNCTION


def convert_measurement(value: float, category: str,
                        from_unit: str, to_unit: str) -> float:

    if category == "Length":
        return convert_length(value, from_unit, to_unit)

    elif category == "Temperature":
        return convert_temperature(value, from_unit, to_unit)

    elif category == "Electrical":
        return convert_electrical(value, from_unit, to_unit)

    elif category == "Power":
        return convert_power(value, from_unit, to_unit)

    raise ValueError("Invalid conversion category")



# ROUTE 1: HOME PAGE

@route
def index(state: State) -> Page:
    return Page(state, [
        Header("Engineering Unit Converter"),
        "Welcome to the Engineering Unit Converter!",
        "Convert measurements in four engineering categories.",
        "",
        Button("Start Converting", "choose_category"),
        Button("View Conversion History", "history"),
        Button("Help and Instructions", "help")
    ])


# ROUTE 2: CATEGORY SELECTION PAGE

@route
def choose_category(state: State) -> Page:
    return Page(state, [
        Header("Choose a Conversion Category"),
        "Select the type of measurement you want to convert:",
        SelectBox(
            "category",
            ["Length", "Temperature", "Electrical", "Power"],
            state.category
        ),
        Button("Continue", "converter"),
        Button("Back to Home", "index")
    ])


# ROUTE 3: CONVERSION FORM PAGE


@route
def converter(state: State, category: str) -> Page:

    # Reset's the units when the category changes
    if category != state.category:
        state.from_unit = ""
        state.to_unit = ""

    state.category = category
    units = get_units(category)

    # Set valid default units
    if state.from_unit not in units:
        state.from_unit = units[0]

    if state.to_unit not in units or state.to_unit == state.from_unit:
        if len(units) > 1:
            state.to_unit = units[1]
        else:
            state.to_unit = units[0]

    state.error_message = ""

    return Page(state, [
        Header("Convert " + category),
        "Enter the measurement you want to convert:",
        TextBox("value", state.value),
        "",
        "Choose the starting unit:",
        SelectBox("from_unit", units, state.from_unit),
        "",
        "Choose the target unit:",
        SelectBox("to_unit", units, state.to_unit),
        "",
        state.error_message,
        Button("Convert Measurement", "convert"),
        Button("Choose Another Category", "choose_category"),
        Button("Home", "index")
    ])



# ROUTE 4: RESULTS PAGE


@route
def convert(state: State, value: str,
            from_unit: str, to_unit: str) -> Page:

    state.value = value
    state.from_unit = from_unit
    state.to_unit = to_unit
    state.error_message = ""
    state.result = ""

    try:
        number = float(value)

        # Checks that the user entered a number
        if value.strip() == "":
            raise ValueError("Please enter a measurement.")

        # Performs the conversion
        answer = convert_measurement(
            number,
            state.category,
            from_unit,
            to_unit
        )

        state.result = str(round(answer, 6))

        # Saves the successful conversion
        record = ConversionRecord(
            number,
            state.category,
            from_unit,
            to_unit,
            answer
        )

        state.history.append(record)

        return Page(state, [
            Header("Conversion Results"),
            "Original measurement: " + str(number) + " " + from_unit,
            "Converted measurement: " + state.result + " " + to_unit,
            "",
            Button("Convert Another Measurement", "choose_category"),
            Button("View Conversion History", "history"),
            Button("Home", "index")
        ])

    except ValueError as error:
        state.error_message = str(error)

        return Page(state, [
            Header("Conversion Error"),
            state.error_message,
            "",
            Button("Try Again", "converter",
                   Argument("category", state.category)),
            Button("Choose Another Category", "choose_category"),
            Button("Home", "index")
        ])



# ROUTE 5: HISTORY PAGE


@route
def history(state: State) -> Page:

    content = [
        Header("Conversion History"),
        "Here are your previous conversions:",
        ""
    ]

    # Checks whether history is empty
    if len(state.history) == 0:
        content.append("You have not completed any conversions yet.")

    else:
        # Display each conversion record
        for record in state.history:
            content.append(
                str(record.value) + " " + record.from_unit
                + " = " + str(round(record.result, 6))
                + " " + record.to_unit
                + " (" + record.category + ")"
            )

    content.extend([
        "",
        Button("Clear History", "clear_history"),
        Button("Start Converting", "choose_category"),
        Button("Home", "index")
    ])

    return Page(state, content)



# ROUTE 6: CLEAR HISTORY

@route
def clear_history(state: State) -> Page:
    state.history = []

    return Page(state, [
        Header("History Cleared"),
        "Your conversion history has been cleared.",
        Button("View History", "history"),
        Button("Home", "index")
    ])



# ROUTE 7: HELP PAGE

@route
def help(state: State) -> Page:
    return Page(state, [
        Header("Help and Instructions"),
        "How to use the Engineering Unit Converter:",
        "",
        "1. Click Start Converting.",
        "2. Select a conversion category.",
        "3. Enter the measurement you want to convert.",
        "4. Select the starting unit.",
        "5. Select the target unit.",
        "6. Click Convert Measurement.",
        "7. View your result.",
        "",
        "Available categories:",
        "Length: Meters, Centimeters, Kilometers",
        "Temperature: Celsius, Fahrenheit, Kelvin",
        "Electrical: Volts, Millivolts, Amperes, Milliamperes",
        "Power: Watts, Kilowatts",
        "",
        "Note: Voltage and current cannot be converted into each other.",
        "",
        Button("Start Converting", "choose_category"),
        Button("Home", "index")
    ])



# START THE WEBSITE

set_website_title("Engineering Unit Converter")

set_site_information(
    author="Logan Beachell",
    description="A website that converts engineering measurements, including length, temperature, electrical measurements, and power.",
    sources="Created using CISC106 course materials, Python, Bakery Tutor LLM, and the Drafter documentation.",
    planning=["CS1 Final Project 1: Design.pdf", "CS1 Final Project 0: Pick a Problem"]
    links=["https://github.com/LoganBeach8/engineering-unit-converter"]
)

hide_debug_information()
set_website_framed(False)

start_server(State())
