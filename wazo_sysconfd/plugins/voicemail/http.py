# Copyright 2022-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from fastapi import APIRouter, Depends

from wazo_sysconfd.plugins.voicemail.asterisk import Asterisk
from .dependencies import get_asterisk

router = APIRouter()


@router.delete('/voicemail', status_code=200)
def delete_voicemail(
    context: str, mailbox: str = None, asterisk: Asterisk = Depends(get_asterisk)
):
    asterisk.delete_voicemail(context, mailbox)


@router.put('/voicemail', status_code=200)
def move_voicemail(
    old_context: str,
    old_mailbox: str,
    new_context: str,
    new_mailbox: str,
    asterisk: Asterisk = Depends(get_asterisk),
):
    asterisk.move_voicemail(
        old_context,
        old_mailbox,
        new_context,
        new_mailbox,
    )
