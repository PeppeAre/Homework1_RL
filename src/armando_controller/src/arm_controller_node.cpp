#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>
#include <sensor_msgs/msg/joint_state.hpp>
#include <std_msgs/msg/float64_multi_array.hpp>
#include <control_msgs/action/follow_joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>

#include <memory>
#include <vector>
#include <string>
#include <functional> 
// ----------------------------------------------------

using namespace std::chrono_literals;

using FollowJointTrajectory = control_msgs::action::FollowJointTrajectory;
using GoalHandleFJT = rclcpp_action::ClientGoalHandle<FollowJointTrajectory>;

class ArmControllerNode : public rclcpp::Node
{
public:
    ArmControllerNode() : Node("arm_controller_node"), current_goal_index_(0)
    {
        this->declare_parameter<std::string>("controller_type", "position");

        joint_state_sub_ = this->create_subscription<sensor_msgs::msg::JointState>(
            "joint_states", 10,
            std::bind(&ArmControllerNode::joint_state_callback, this, std::placeholders::_1));

        // Publisher per il controller di posizione (Punto 4c)
        position_cmd_pub_ = this->create_publisher<std_msgs::msg::Float64MultiArray>(
            "/simple_position_controller/commands", 10); 

        // Action Client per il controller di traiettoria (Punto 4d)
        trajectory_action_client_ = rclcpp_action::create_client<FollowJointTrajectory>(
            this, "/joint_trajectory_controller/follow_joint_trajectory"); 

        goals_ = {
            {0.0, 0.0, 0.0, 0.0},
            {0.5, 0.2, 0.2, 0.0},
            {-0.5, -0.2, -0.2, 0.0},
            {0.0, 0.5, 0.5, 0.5}
        };

        timer_ = this->create_wall_timer(
            3000ms, std::bind(&ArmControllerNode::send_sequential_commands, this));

        RCLCPP_INFO(this->get_logger(), "arm_controller_node avviato.");
    }

private:
    void joint_state_callback(const sensor_msgs::msg::JointState::SharedPtr msg)
    {
        // Limitiamo il log per non affollare il terminale
        RCLCPP_INFO_ONCE(this->get_logger(), "Posizioni attuali (j0, j1, j2, j3): [%.2f, %.2f, %.2f, %.2f]",
                    msg->position[0], msg->position[1], msg->position[2], msg->position[3]);
    }

    void send_sequential_commands()
    {
        std::string controller_type = this->get_parameter("controller_type").as_string();
        if (goals_.empty()) return;

        std::vector<double> current_goal = goals_[current_goal_index_];
        current_goal_index_ = (current_goal_index_ + 1) % goals_.size();

        RCLCPP_INFO(this->get_logger(), "Invio goal %ld usando '%s' controller: [%.2f, %.2f, %.2f, %.2f]",
            current_goal_index_, controller_type.c_str(), 
            current_goal[0], current_goal[1], current_goal[2], current_goal[3]);

        if (controller_type == "position")
        {
            publish_position_command(current_goal);
        }
        else if (controller_type == "trajectory")
        {
            send_trajectory_goal(current_goal);
        }
        else
        {
            RCLCPP_WARN(this->get_logger(), "Tipo controller '%s' non riconosciuto. Usare 'position' o 'trajectory'.", controller_type.c_str());
        }
    }

    void publish_position_command(const std::vector<double>& positions)
    {
        auto msg = std_msgs::msg::Float64MultiArray();
        msg.data = positions;
        position_cmd_pub_->publish(msg);
    }

    void send_trajectory_goal(const std::vector<double>& positions)
    {
        if (!trajectory_action_client_->action_server_is_ready())
        {
            RCLCPP_ERROR(this->get_logger(), "Action server (/joint_trajectory_controller) non disponibile.");
            current_goal_index_ = (current_goal_index_ + goals_.size() - 1) % goals_.size();
            return;
        }

        auto goal_msg = FollowJointTrajectory::Goal();
        goal_msg.trajectory.joint_names = {"j0", "j1", "j2", "j3"};

        trajectory_msgs::msg::JointTrajectoryPoint point;
        point.positions = positions;
        point.time_from_start = rclcpp::Duration::from_seconds(1.5); 

        goal_msg.trajectory.points.push_back(point);

        RCLCPP_INFO(this->get_logger(), "Invio goal di traiettoria...");
        trajectory_action_client_->async_send_goal(goal_msg);
    }

    rclcpp::Subscription<sensor_msgs::msg::JointState>::SharedPtr joint_state_sub_;
    rclcpp::Publisher<std_msgs::msg::Float64MultiArray>::SharedPtr position_cmd_pub_;
    rclcpp_action::Client<FollowJointTrajectory>::SharedPtr trajectory_action_client_;

    rclcpp::TimerBase::SharedPtr timer_;
    
    std::vector<std::vector<double>> goals_;
    size_t current_goal_index_;
};

int main(int argc, char* argv[])
{
    rclcpp::init(argc, argv);
    auto arm_controller_node = std::make_shared<ArmControllerNode>();

    //MultiThreadedExecutor per evitare che il subscriber blocchi il timer
    rclcpp::executors::MultiThreadedExecutor executor;
    executor.add_node(arm_controller_node);
    
    RCLCPP_INFO(arm_controller_node->get_logger(), "Avvio MultiThreadedExecutor...");
    executor.spin();

    rclcpp::shutdown();
    return 0;
}
