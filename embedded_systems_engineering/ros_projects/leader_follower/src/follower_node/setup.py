from setuptools import setup

package_name = "follower_node"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Student",
    maintainer_email="student@example.com",
    description="Follower robot node for leader-follower multi-robot system",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "follower_node = follower_node.follower_node:main",
            "follower_node_skeleton = follower_node.follower_node_skeleton:main",
        ],
    },
)
