#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

"""
CRT Bot メインアプリケーション
Flask/aiohttp アプリケーションエントリーポイントと Bot Framework 統合
"""

import sys
import traceback
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import TurnContext
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication
from botbuilder.schema import Activity, ActivityTypes

from config import DefaultConfig
from bot import Bot

# 設定とアダプターの初期化
CONFIG = DefaultConfig()
ADAPTER = CloudAdapter(ConfigurationBotFrameworkAuthentication(CONFIG))


async def on_error(context: TurnContext, error: Exception):
    """
    Bot のエラーハンドラー

    Args:
        context: Bot Framework のターンコンテキスト
        error: 発生したエラー
    """
    print(f"\n [on_turn_error] unhandled error: {error}", file=sys.stderr)
    traceback.print_exc()
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity("To continue to run this bot, please fix the bot source code.")

    # エミュレーターの場合はトレースアクティビティを送信
    if context.activity.channel_id == "emulator":
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

# Bot インスタンスを作成
BOT = Bot()


async def messages(req: Request) -> Response:
    """
    Bot Framework メッセージエンドポイント

    Args:
        req: HTTP リクエスト

    Returns:
        HTTP レスポンス
    """
    return await ADAPTER.process(req, BOT)


async def root(req: Request) -> Response:
    """
    ルートエンドポイント（ヘルスチェック用）

    Args:
        req: HTTP リクエスト

    Returns:
        HTTP レスポンス
    """
    return Response(text="Teams Task Management Bot with Azure DevOps Integration", content_type='text/html')


# aiohttp アプリケーションを作成
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/", root)

if __name__ == "__main__":
    import os
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "3978"))
    web.run_app(APP, host=host, port=port)
