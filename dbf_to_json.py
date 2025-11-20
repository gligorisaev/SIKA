#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DBF to JSON converter for Clipper ERP databases
Converts DBF files to JSON format for web dashboard
"""

import struct
import json
import datetime
from pathlib import Path

class DBFReader:
    """Simple DBF reader without external dependencies"""
    
    def __init__(self, filename, encoding='cp852'):
        self.filename = filename
        self.encoding = encoding
        self.records = []
        self.fields = []
        
    def read(self):
        """Read DBF file and parse records"""
        with open(self.filename, 'rb') as f:
            # Read header
            version = struct.unpack('B', f.read(1))[0]
            year, month, day = struct.unpack('BBB', f.read(3))
            num_records = struct.unpack('<I', f.read(4))[0]
            header_length = struct.unpack('<H', f.read(2))[0]
            record_length = struct.unpack('<H', f.read(2))[0]
            
            f.seek(32)  # Skip to field definitions
            
            # Read field definitions
            while True:
                field_data = f.read(32)
                if field_data[0] == 0x0D:  # End of field definitions
                    break
                    
                field_name = field_data[0:11].split(b'\x00')[0].decode(self.encoding)
                field_type = chr(field_data[11])
                field_length = field_data[16]
                field_decimal = field_data[17]
                
                self.fields.append({
                    'name': field_name,
                    'type': field_type,
                    'length': field_length,
                    'decimal': field_decimal
                })
            
            # Read records
            f.seek(header_length)
            for _ in range(num_records):
                record_data = f.read(record_length)
                if record_data[0] != 0x2A:  # Not deleted
                    record = self._parse_record(record_data[1:])
                    self.records.append(record)
                    
        return self.records
    
    def _parse_record(self, data):
        """Parse a single record"""
        record = {}
        pos = 0
        
        for field in self.fields:
            field_data = data[pos:pos + field['length']]
            pos += field['length']
            
            try:
                if field['type'] == 'C':  # Character
                    value = field_data.decode(self.encoding).strip()
                elif field['type'] == 'N':  # Numeric
                    value_str = field_data.decode('ascii').strip()
                    if value_str:
                        if field['decimal'] > 0:
                            value = float(value_str)
                        else:
                            value = int(value_str)
                    else:
                        value = None
                elif field['type'] == 'D':  # Date
                    date_str = field_data.decode('ascii').strip()
                    if date_str and len(date_str) == 8:
                        year = int(date_str[0:4])
                        month = int(date_str[4:6])
                        day = int(date_str[6:8])
                        value = f"{year:04d}-{month:02d}-{day:02d}"
                    else:
                        value = None
                elif field['type'] == 'L':  # Logical
                    value = field_data[0] in (ord('T'), ord('t'), ord('Y'), ord('y'))
                else:
                    value = field_data.decode(self.encoding).strip()
                    
                record[field['name']] = value
            except:
                record[field['name']] = None
                
        return record

def convert_dbf_to_json(dbf_file, json_file=None, encoding='cp852', limit=None):
    """
    Convert DBF file to JSON
    
    Args:
        dbf_file: Path to DBF file
        json_file: Path to output JSON file (optional)
        encoding: Character encoding (default: cp852 for Cyrillic)
        limit: Limit number of records (optional)
    """
    reader = DBFReader(dbf_file, encoding)
    records = reader.read()
    
    if limit:
        records = records[:limit]
    
    data = {
        'fields': reader.fields,
        'records': records,
        'total_records': len(records)
    }
    
    if json_file:
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Converted {len(records)} records to {json_file}")
    
    return data

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dbf_to_json.py <dbf_file> [json_file] [limit]")
        print("Example: python dbf_to_json.py NASLOV.DBF naslov.json 1000")
        sys.exit(1)
    
    dbf_file = sys.argv[1]
    json_file = sys.argv[2] if len(sys.argv) > 2 else dbf_file.replace('.DBF', '.json').replace('.dbf', '.json')
    limit = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    convert_dbf_to_json(dbf_file, json_file, limit=limit)
