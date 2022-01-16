// Copyright 2020 Espressif Systems (Shanghai) Co. Ltd.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include <stdio.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "iot_servo.h"
#include "unity.h"
#include "sdkconfig.h"

#ifdef CONFIG_IDF_TARGET_ESP32
#define SERVO_CH0_PIN 26

#endif

float aim_angle = 45;

void motor_set_angle(float angle)
{
    aim_angle = angle;
    // iot_servo_write_angle(LEDC_LOW_SPEED_MODE, 0, aim_angle);
}

float motor_read_angle(void)
{
    float angle_ls;
    iot_servo_read_angle(LEDC_LOW_SPEED_MODE, 0, &angle_ls);
    // printf("angle: %f\n", angle);
    return angle_ls;
}

void motor_pid_task()
{
    // 使用 位置式 PID 控制 舵机角度
    
    // PID 参数
    float kp = 0.2;
    float ki = 0.03;
    float kd = 0.001;
    float error_last = 0;
    float error_sum = 0;
    float error_now = 0;

    // 设置 PID 输出限制
    float output_max = 179;
    float output_min = 1;

    float output = 0;

    // 设置 PID 算法的时间间隔
    float dt = 0.1; //10ms

    // PID 算法
    while (1)
    {
        // 读取当前角度
        float angle_now = motor_read_angle();

        // 计算误差
        error_now = aim_angle - angle_now;

        // 计算误差积分
        error_sum += error_now * dt;

        // 计算误差微分
        float error_diff = (error_now - error_last) / dt;

        // 计算 PID 输出
        output = kp * error_now + ki * error_sum + kd * error_diff;

        output =  angle_now + output;
        // 输出限制
        if (output > output_max)
        {
            output = output_max;
        }
        else if (output < output_min)
        {
            output = output_min;
        }

        // 设置 PID 输出
        iot_servo_write_angle(LEDC_LOW_SPEED_MODE, 0, output);

        // 更新误差
        error_last = error_now;
        printf("angle: %f, aim: %f, output: %f\n", angle_now, aim_angle, output);

        // 等待时间间隔
        vTaskDelay(dt*1000 / portTICK_PERIOD_MS);
    }
}

void motor_init()
{
    servo_config_t servo_cfg_ls = {
        .max_angle = 180,
        .min_width_us = 500,
        .max_width_us = 2500,
        .freq = 250,
        .timer_number = LEDC_TIMER_0,
        .channels = {
            .servo_pin = {
                SERVO_CH0_PIN,
            },
            .ch = {
                LEDC_CHANNEL_0,
            },
        },
        .channel_number = 1,
    } ;
    TEST_ASSERT(ESP_OK == iot_servo_init(LEDC_LOW_SPEED_MODE, &servo_cfg_ls));
}

void motor_test()
{
    size_t i;
    float angle_ls;
    for (i = 0; i <= 18000; i++) {
        motor_set_angle(abs(i%3600 - 1800)/10.0);

        vTaskDelay(10 / portTICK_PERIOD_MS);
        angle_ls = motor_read_angle();
        ESP_LOGI("servo", "[%d|%.2f]", i, angle_ls);

    }

    iot_servo_deinit(LEDC_LOW_SPEED_MODE);
}

void console_init();


void register_motor_cmd_line(void);
int app_main()
{
    console_init();   
    motor_init();
    register_motor_cmd_line();
    xTaskCreate(motor_pid_task, "motor_pid_task", 2048, NULL, 5, NULL);
    // motor_test();

    return 0;
}

