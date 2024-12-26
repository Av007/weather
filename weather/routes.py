from flask import Blueprint, jsonify, render_template, request, send_file, make_response
import io
from .weather import Weather

main_blueprint = Blueprint('main', __name__)

weather = Weather()


@main_blueprint.route('/', methods=['GET'])
def index():
    """
    Index web page
    :return: str
    """
    return render_template('index/index.html')


@main_blueprint.route('/api/weather', methods=['GET'])
def get_weather():
    """
    Fetches weather data from the public API and returns it as JSON.
    """
    filters = request.args.get('filters')
    data = weather.scrape_data(filters)
    return jsonify({
        "status": "success",
        "data": data,
    })


@main_blueprint.route('/graph', methods=['GET'])
def graph():
    """Generate a plot with a varying number of randomly generated points"""
    fig = weather.get_image_graph()

    if not fig:
        return make_response('File not found', 404)

    img = io.StringIO()
    fig.savefig(img, format='svg')

    svg_img = '<svg' + img.getvalue().split('<svg')[1]
    return svg_img


@main_blueprint.route('/download', methods=['GET'])
def download_file():
    file = weather.download()
    return send_file(file, as_attachment=True)
