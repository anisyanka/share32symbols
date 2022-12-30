#include "main.h"
#include "init.h"
#include "usb_device.h"
#include "usbd_cdc_if.h"
#include "ws0010.h"

#include <stdio.h>
#include <string.h>
#include <stdbool.h>

uint8_t ok_ans[] = { 'O', 'K' };
uint8_t err_ans[] = { 'N', 'O' };
bool is_package_received = false;
uint8_t user_rx_buffer[APP_USER_RX_BUFFER_SIZE] = { 0 };
uint32_t rx_len = 0;

ws0010_ll_t oled_ll_func = { 0 };
ws0010_dev_t oled_dev = {
	.line_count = 2,
	.displayed_symbols_per_line = 16,
	.max_symbols_per_line = 64,
	.font_size = WS0010_5x8_DOTS,
	.interface_bits = WS0010_8_BITS,
	.alphabet = ENG_RUS,
	.ll = &oled_ll_func,
};

static void oled_delay_us(uint32_t)
{
	/* HARDCODE */
	HAL_Delay(5);
}

static void oled_out_bits(uint8_t value)
{
	GPIOA->ODR = value;
}

static void oled_set_rs(void)
{
	HAL_GPIO_WritePin(OLED_RS_GPIO_Port, OLED_RS_Pin, GPIO_PIN_SET);
}

static void oled_reset_rs(void)
{
	HAL_GPIO_WritePin(OLED_RS_GPIO_Port, OLED_RS_Pin, GPIO_PIN_RESET);
}

static void oled_set_rw(void)
{
	HAL_GPIO_WritePin(OLED_RW_GPIO_Port, OLED_RW_Pin, GPIO_PIN_SET);
}

static void oled_reset_rw(void)
{
	HAL_GPIO_WritePin(OLED_RW_GPIO_Port, OLED_RW_Pin, GPIO_PIN_RESET);
}

static void oled_set_e(void)
{
	HAL_GPIO_WritePin(OLED_E_GPIO_Port, OLED_E_Pin, GPIO_PIN_SET);
}

static void oled_reset_e(void)
{
	HAL_GPIO_WritePin(OLED_E_GPIO_Port, OLED_E_Pin, GPIO_PIN_RESET);
}

int main(void)
{
	HAL_Init();
	SystemClock_Config();
	GPIO_Init();
	USB_DEVICE_Init();
	USART1_UART_Init();

	oled_ll_func.delay_us = oled_delay_us;
	oled_ll_func.set_bits_to_out_pins = oled_out_bits;
	oled_ll_func.set_rs = oled_set_rs;
	oled_ll_func.reset_rs = oled_reset_rs;
	oled_ll_func.set_rw = oled_set_rw;
	oled_ll_func.reset_rw = oled_reset_rw;
	oled_ll_func.set_e = oled_set_e;
	oled_ll_func.reset_e = oled_reset_e;

	char line1[APP_USER_RX_BUFFER_SIZE] = "Share 32 symbols";
	char line2[APP_USER_RX_BUFFER_SIZE] = "     (^-^)/     ";

	ws0010_init(&oled_dev);

	ws0010_set_ddram_addr(&oled_dev, 0);
	ws0010_print(&oled_dev, line1, strlen(line1));

	ws0010_set_ddram_addr(&oled_dev, 0x40);
	ws0010_print(&oled_dev, line2, strlen(line2));

	while (1)
	{
		if (is_package_received)
		{
			is_package_received = false;
			CDC_Transmit_FS(ok_ans, sizeof(ok_ans));

			int is_new_line = 0;
			int line1_indx = 0;
			int line2_indx = 0;

			for (uint32_t i = 0; i < rx_len; ++i)
			{
				/* wait for the delimiter between lines */
				if (user_rx_buffer[i] == APP_OLED_LINE_DELIMITER)
				{
					is_new_line = 1;
					continue;
				}

				if (is_new_line)
				{
					line2[line2_indx++] = user_rx_buffer[i];
				}
				else
				{
					line1[line1_indx++] = user_rx_buffer[i];
				}
			}

			ws0010_clear(&oled_dev);
			ws0010_home(&oled_dev);

			ws0010_set_ddram_addr(&oled_dev, 0x00);
			ws0010_print(&oled_dev, line1, line1_indx);

			ws0010_set_ddram_addr(&oled_dev, 0x40);
			ws0010_print(&oled_dev, line2, line2_indx);
			HAL_Delay(5000);
		}

		ws0010_scroll_display_left(&oled_dev);
		HAL_Delay(80);
	}
}

void Error_Handler(void)
{
	/* User can add his own implementation to report the HAL error return state */
	__disable_irq();
	while (1)
	{
	}
}

#ifdef  USE_FULL_ASSERT
/**
	* @brief  Reports the name of the source file and the source line number
	*         where the assert_param error has occurred.
	* @param  file: pointer to the source file name
	* @param  line: assert_param error line source number
	* @retval None
	*/
void assert_failed(uint8_t *file, uint32_t line)
{
	/* User can add his own implementation to report the file name and line number,
		 ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
}
#endif /* USE_FULL_ASSERT */
