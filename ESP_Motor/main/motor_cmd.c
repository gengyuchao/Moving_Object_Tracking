#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <unistd.h>
#include "esp_log.h"
#include "esp_console.h"
#include "esp_system.h"
#include "driver/uart.h"
#include "argtable3/argtable3.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

void motor_set_angle(float angle);
float motor_read_angle(void);

static float motor_angle = 0;


static struct {
    struct arg_str *cmd_srt;
    struct arg_dbl *value;
    struct arg_end *end;
} motor_cmd_line_args;

/**
 * @brief 电机驱动命令处理函数
 * 
 * @param argc 
 * @param argv 
 * @return int 
 */
static int motor_cmd_line_handler(int argc, char **argv)
{
    int nerrors = arg_parse(argc, argv, (void **) &motor_cmd_line_args);
    if (nerrors != 0) {
        arg_print_errors(stderr, motor_cmd_line_args.end, argv[0]);
        return 1;
    }

    if (motor_cmd_line_args.cmd_srt->count != 0)
    {
        if (strcmp(motor_cmd_line_args.cmd_srt->sval[0], "turn_left") == 0)
        {
            motor_angle = motor_read_angle() - motor_cmd_line_args.value->dval[0];;
            // printf("motor turn left\n");
        }
        else if (strcmp(motor_cmd_line_args.cmd_srt->sval[0], "turn_right") == 0)
        {
            motor_angle = motor_read_angle() + motor_cmd_line_args.value->dval[0];;
            // printf("motor turn right\n");
        }
        else if (strcmp(motor_cmd_line_args.cmd_srt->sval[0], "set_angle") == 0)
        {
            motor_angle = motor_cmd_line_args.value->dval[0];
            // printf("motor set_angle\n");
        }
        else
        {
            printf("motor cmd error\n");
        }
        // printf("curr motor angle: %f,set to: %f\n", motor_read_angle(), motor_angle);
        motor_set_angle(motor_angle);
    }

    return 0;
}

/**
 * @brief 电机驱动命令注册函数
 * 
 */
void register_motor_cmd_line(void)
{
    motor_cmd_line_args.cmd_srt = arg_str1(NULL,NULL,"<turn_left,turn_right,set_angle>","motor direction,angle");
    motor_cmd_line_args.value = arg_dbl1(NULL,NULL,"<value>","set value");
    motor_cmd_line_args.end = arg_end(1);

    const esp_console_cmd_t cmd = {
        .command = "motor",
        .help = "motor cmd",
        .hint = NULL,
        .func = &motor_cmd_line_handler,
        .argtable = &motor_cmd_line_args
    };
    ESP_ERROR_CHECK( esp_console_cmd_register(&cmd) );
}  
