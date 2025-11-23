#!/usr/bin/env python3
"""
CS2 Inspect Backend Service
Handles !g gen codes and inspect links, returns JSON for CounterStrikeSharp plugin
"""

from flask import Flask, request, jsonify
import cs2inspect
import re
import urllib.parse
import os
import os

app = Flask(__name__)

def parse_inspect_link(link):
    """Parse a steam:// inspect link and extract item info"""
    try:
        # Decode URL
        decoded = urllib.parse.unquote(link)
        print(f"Parsing inspect link: {decoded[:100]}...")
        
        # Try to parse as inspect link
        # Format: steam://rungame/730/.../+csgo_econ_action_preview S[SteamID]A[AssetID]D[DefIndex]
        match = re.match(r'steam://rungame/730/\d+/[+ ]csgo_econ_action_preview ([SM])(\d+)A(\d+)D(\d+)', decoded)
        if match:
            asset_id = match.group(3)
            def_index = int(match.group(4))
            print(f"Extracted: asset_id={asset_id}, def_index={def_index}")
            
            # Note: Inspect links don't contain paint info, only defindex
            # To get paint info, you'd need to query Steam Game Coordinator
            # For now, return defindex only - paint info must come from gen code
            return {
                "defindex": def_index,
                "paintindex": 0,  # Not available in inspect link alone
                "paintseed": 0,
                "floatvalue": 0.0,
                "itemid": asset_id
            }
        else:
            print(f"No match found for inspect link pattern")
    except Exception as e:
        print(f"Error parsing inspect link: {e}")
        import traceback
        traceback.print_exc()
    return None

def parse_gen_code(code):
    """Parse a !g gen code and extract item info"""
    try:
        # Remove !g prefix if present
        if code.startswith("!g "):
            code = code[3:].strip()
        
        # Gen code format: defindex paintindex seed float ...
        parts = code.split()
        if len(parts) >= 4:
            defindex = int(parts[0])
            paintindex = int(parts[1])
            seed = int(parts[2])
            floatvalue = float(parts[3])
            
            return {
                "defindex": defindex,
                "paintindex": paintindex,
                "paintseed": seed,
                "floatvalue": floatvalue,
                "itemid": "0"
            }
    except Exception as e:
        print(f"Error parsing gen code: {e}")
    return None

@app.route('/', methods=['GET'])
def inspect():
    """Handle inspect requests"""
    try:
        url_param = request.args.get('url', '')
        print(f"Received request: url={url_param[:100]}...")
        
        if not url_param:
            return jsonify({"error": "Missing url parameter"}), 400
        
        # Check if it's a gen code (!g ...)
        if url_param.startswith("!g"):
            print("Parsing as gen code")
            item_info = parse_gen_code(url_param)
        # Check if it's an inspect link
        elif url_param.startswith("steam://"):
            print("Parsing as inspect link")
            item_info = parse_inspect_link(url_param)
        else:
            return jsonify({"error": "Invalid format. Use !g code or steam:// link"}), 400
        
        if not item_info:
            return jsonify({"error": "Failed to parse item info"}), 400
        
        print(f"Returning item info: {item_info}")
        
        # Return in cs2-inspect-service format
        return jsonify({
            "iteminfo": {
                "defindex": item_info["defindex"],
                "paintindex": item_info["paintindex"],
                "paintseed": item_info["paintseed"],
                "floatvalue": item_info["floatvalue"],
                "itemid": item_info["itemid"],
                "rarity": 4,
                "quality": 4,
                "origin": 8
            }
        })
    except Exception as e:
        print(f"Error in inspect endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    # For local development - Render uses PORT env var
    port = int(os.environ.get('PORT', 3000))
    print("=" * 60)
    print("CS2 Inspect Backend Service")
    print("=" * 60)
    print(f"Starting on port {port}")
    print("\nEndpoints:")
    print("  GET /?url=!g <code> - Parse gen code")
    print("  GET /?url=steam://... - Parse inspect link")
    print("  GET /health - Health check")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    try:
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()

