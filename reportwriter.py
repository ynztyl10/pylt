#!/usr/bin/env python


def write_initial_html(file_handle):
    file_handle.write("""\
<!DOCTYPE html 
     PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN"
     "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
    <title>Pylot - Results</title>
    <meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
    <meta http-equiv="Content-Language" content="en" />
    <style type="text/css">
        body {
            background-color: #FFFFFF;
            color: #000000;
            font-family: Arial, Verdana, Helvetica, sans-serif;
            font-size: 12px;
            padding: 10px;
            }
        h1 {
            font-size: 16px;
            margin-bottom: 0.5em;
            background: #FF9933;
            padding-left: 5px;
            padding-top: 2px;
            }
        h2 {
            font-size: 14px;
            margin-bottom: 0.5em;
            }
        h3 {
            font-size: 13px;
            margin-bottom: 2em;
            background: #F0F0F0;
            margin-top: 3em;
            margin-bottom: 1em;
            }
        h4 {
            font-size: 11px;
            margin-bottom: 0.5em;
            }
        table {
            font-size: 11px;
            border: 1px solid;
            margin-bottom: 1.2em;
            }
        td {
            text-align: right;
            padding-right: 10px;
            color: #000000;
            background: #FFFFFF;
            }
        th {
            text-align: right;
            padding-right: 8px;
            padding-left: 4px;
            color: #000000;
            background: #F0F0F0;
            }
        a:link {
            color: #335eb3;
            text-decoration: underline;
        }
        a:visited { 
            color: #335eb3;
            text-decoration: underline;  
        }
        a:hover { 
            color: #003399;
            text-decoration: underline;  
        }
    </style>
</head>
<body>
<h1>Pylot - Web Performance Results</h1>
""")
    
    

def write_closing_html(file_handle):
    file_handle.write("""\
</body>
</html>
    """)




