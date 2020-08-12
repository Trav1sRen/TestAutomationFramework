from setuptools import setup, find_packages

setup(
    name='test_automation_framework',
    version='1.0.0',

    url="https://github.com/Trav1sRen/TestAutomationFramework",
    author='Travis Ren',

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[
        'lxml', 'requests', 'xmltodict',
        'selenium', 'Appium-Python-Client']  # Rmb to add new dependencies into here
)
