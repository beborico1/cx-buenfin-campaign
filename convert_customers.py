#!/usr/bin/env python3
"""
Convert EcomSend customer export to plantilla-clientes format
"""
import csv

SOURCE_FILE = '/Users/luisrico/dev/cx/buenfin/EcomSend_customers_export_1762410755.csv'
OUTPUT_FILE = '/Users/luisrico/dev/cx/buenfin/plantilla-clientes-filled.csv'

def split_name(full_name):
    """Split full name into first name and last name"""
    parts = full_name.strip().split(maxsplit=1)
    if len(parts) == 2:
        return parts[0], parts[1]
    elif len(parts) == 1:
        return parts[0], ""
    return "", ""

def extract_location_info(location):
    """Extract location information"""
    if not location or location == '-':
        return "52", ""  # Default to Mexico country code
    # Most entries seem to be "City, Mexico"
    return "52", location

def clean_phone(phone):
    """Clean phone number"""
    if not phone or phone == '-':
        return ""
    # Remove + and country code if present
    phone = phone.replace('+', '').replace('-', '').replace(' ', '')
    # If starts with 52, keep just the 10 digits after
    if phone.startswith('52') and len(phone) > 10:
        return phone[2:]
    return phone[-10:] if len(phone) >= 10 else phone

def format_whatsapp(phone):
    """Format phone for WhatsApp (with country code)"""
    if not phone:
        return ""
    clean = clean_phone(phone)
    if clean:
        return f"521{clean}" if len(clean) == 10 else f"52{clean}"
    return ""

def convert_customers():
    """Convert customer data"""
    customers_converted = 0

    # Read source file
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        # Handle BOM if present
        content = f.read()
        if content.startswith('\ufeff'):
            content = content[1:]

        reader = csv.DictReader(content.splitlines())

        # Write to output file
        with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as out_f:
            fieldnames = ['nombre', 'apellidos', 'telefono', 'whatsapp', 'pais', 'email',
                         'presupuesto', 'estado_civil', 'genero', 'ocupacion', 'ingreso',
                         'nombre_conyuge', 'telefono_conyuge', 'ocupacion_conyuge',
                         'ingreso_conyuge', 'notas']

            writer = csv.DictWriter(out_f, fieldnames=fieldnames)
            writer.writeheader()

            for row in reader:
                # Split name
                nombre, apellidos = split_name(row['Customer name'])

                # Clean phone
                telefono = clean_phone(row.get('Phone number', ''))
                whatsapp = format_whatsapp(row.get('Phone number', ''))

                # Get location info
                pais, location_full = extract_location_info(row.get('Location', ''))

                # Create output row
                output_row = {
                    'nombre': nombre,
                    'apellidos': apellidos,
                    'telefono': telefono,
                    'whatsapp': whatsapp,
                    'pais': pais,
                    'email': row['Email address'],
                    'presupuesto': '',  # Empty - not in source data
                    'estado_civil': '',  # Empty - not in source data
                    'genero': '',  # Empty - not in source data
                    'ocupacion': '',  # Empty - not in source data
                    'ingreso': '',  # Empty - not in source data
                    'nombre_conyuge': '',  # Empty - not in source data
                    'telefono_conyuge': '',  # Empty - not in source data
                    'ocupacion_conyuge': '',  # Empty - not in source data
                    'ingreso_conyuge': '',  # Empty - not in source data
                    'notas': f"Subscribed via {row.get('Popup', 'popup')} on {row.get('Subscription date', '')}"
                }

                writer.writerow(output_row)
                customers_converted += 1

                if customers_converted % 1000 == 0:
                    print(f"Converted {customers_converted} customers...")

    print(f"\n✓ Conversion complete!")
    print(f"Total customers converted: {customers_converted}")
    print(f"Output file: {OUTPUT_FILE}")

if __name__ == '__main__':
    convert_customers()
