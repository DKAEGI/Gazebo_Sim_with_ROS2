import rclpy
import time
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class ObstacleAvoidance(Node):
    def __init__(self):
        super().__init__('obstacle_avoidance') ## name of the node
        self.get_logger().info("Starting Obstacle Avoidance...")
        # Publisher
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 40)
        # Subscriber
        self.subscription=self.create_subscription(LaserScan,'/scan',self.get_scan_values,40)
        # Periodic publisher call
        timer_period = 0.2;self.timer = self.create_timer(timer_period, self.send_cmd_vel)
        # Value for linear velocity
        self.linear_vel = 0.22 
        # Making dictionary to divide the area of laser scans
        self.regions={'right':[],'front':[],'left':[],'back':[]}
        # Creating a message object to fit new velocities and publish them
        self.velocity=Twist()
        # Threshold for laserbeam
        self.threshold = 0.9;


    ## Subscriber Callback function 
    def get_scan_values(self,scan_data):
        # 720 data points dividing them in 4 regions
        # If there is something in the region get the smallest value
        back_ranges = scan_data.ranges[0:90] + scan_data.ranges[630:720]
        self.regions = {
        'right':   round(float(min(min(scan_data.ranges[90:270]), 100)),2),
        'front':   round(float(min(min(scan_data.ranges[270:450]), 100)),2),
        'left':    round(float(min(min(scan_data.ranges[450:630]), 100)),2),
        'back':    round(float(min(min(back_ranges), 100)),2),
        }
        print(self.regions['left']," / ",self.regions['front']," / ",self.regions['right']," / ",self.regions['back'])

  
    ## Callback Publisher of velocities called every 0.2 seconds
    def send_cmd_vel(self):
        # Set of linear velocity
        self.velocity.linear.x=self.linear_vel
        # Set of angular velocity
        if(self.regions['front'] > self.threshold):
            self.velocity.angular.z=0.0 # Go primary forward
            print("forward")
        elif(self.regions['right'] > self.threshold and self.regions['front'] < self.threshold):
            self.velocity.angular.z=-1.57 # Go secondary right
            print("right")
        elif(self.regions['left'] > self.threshold and self.regions['front'] < self.threshold  and self.regions['right'] < self.threshold ):
            self.velocity.angular.z=1.57 # Go left, if forward and right is not possible
            print("left")          
        elif(self.regions['left'] < self.threshold and self.regions['front'] < self.threshold  and self.regions['right'] < self.threshold and self.regions['back'] > self.threshold):
            self.velocity.angular.z=3.14 # Take full turn
            print("180 degrees turn")
        else: #Add more conditions  to make it more robust
            print("Some other conditions are required to be programmed") 
       
        # Publish velocity
        self.publisher.publish(self.velocity)

def main(args=None):

    # Wait for gazebo GUI to launch and display the world
    time.sleep(10.0)
        
    rclpy.init(args=args)
    node=ObstacleAvoidance()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()