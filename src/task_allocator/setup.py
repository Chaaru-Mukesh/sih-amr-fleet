from setuptools import find_packages, setup

package_name = 'task_allocator'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='chaaru',
    maintainer_email='chaaru@todo.todo',
    description='Task allocator for multi-robot fleet',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'task_allocator_node = task_allocator.task_allocator_node:main',
        ],
    },
)

