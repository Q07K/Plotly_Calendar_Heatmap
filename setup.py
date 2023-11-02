from setuptools import setup, find_packages

setup(
    name='CalendarHeatmap',
    version='1.0.0',
    description='plotly CalendarHeatmap function',
    url='https://github.com/Q07K/Plotly_Calendar_Heatmap',
    author='Kim Gyuheong',
    author_email='kgh0730@gmail.com',
    license='None',
    packages=find_packages(),
    install_requires=['pandas', 'plotly']
)