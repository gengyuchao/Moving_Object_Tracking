/* Console example — declarations of command registration functions.

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#pragma once

#ifdef __cplusplus
extern "C" {
#endif

typedef void (*func_type)(void);
//command & func list 
typedef struct {
    char* cmd_name;
    func_type func;
}cmd_list_t;

void register_cmd_in_list(cmd_list_t* cmd);

#ifdef __cplusplus
}
#endif
