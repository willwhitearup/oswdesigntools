from flask import Flask, render_template, flash, jsonify, request, session



app = Flask(__name__)

@app.route('/gc', methods=['GET', 'POST'])
def gc_route():
    if request.method == 'POST':
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        form_data = data.get('form_data', {})
        print(form_data)

        return jsonify({'message': 'Plot updated successfully'})

    # If GET request
    return render_template('gc.html')

