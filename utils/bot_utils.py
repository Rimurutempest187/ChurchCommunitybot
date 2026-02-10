import logging

async def error_handler(update, context):
    logging.error(f"Update {update} caused error {context.error}")
