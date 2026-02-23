from flask import Flask, render_template, flash, jsonify, request, session


app = Flask(__name__)

@app.route('/boltedconn', methods=['GET', 'POST'])
def boltedconn_route():
    if request.method == 'POST':
        data = request.get_json()

        if not data:
            return jsonify({'error': 'No JSON received'}), 400

        form_data = data.get('form_data', {})
        # print(form_data)

        return jsonify({'message': 'success'
                        })

    return render_template('boltedconn.html'
                           )
