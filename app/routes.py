from flask import Blueprint, jsonify, render_template, request, Response
import io

from app.models import Weather

main_blueprint = Blueprint('main', __name__)


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
    weather = Weather()
    data = weather.scrape_data(filters)
    return jsonify({
        "status": "success",
        "data": data,
    })

@main_blueprint.route('/graph', methods=['GET'])
def graph():
    """Generate a plot with a varying number of randomly generated points"""
    weather = Weather()
    fig = weather.get_image_graph()
    img = io.StringIO()
    fig.savefig(img, format='svg')

    svg_img = '<svg' + img.getvalue().split('<svg')[1]
    return svg_img
