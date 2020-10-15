import time
import uuid

import click
from fate_test._client import Clients
from fate_test._io import LOGGER, echo
from fate_test.scripts._utils import _upload_data, _load_testsuites, _delete_data


@click.group(name="data")
def data_group():
    """
    upload or delete data in suite config files
    """
    ...


@data_group.command("upload")
@click.option('-i', '--include', required=True, type=click.Path(exists=True), multiple=True, metavar="<include>",
              help="include *benchmark.json under these paths")
@click.option('-e', '--exclude', type=click.Path(exists=True), multiple=True,
              help="exclude *benchmark.json under these paths")
@click.option('-g', '--glob', type=str,
              help="glob string to filter sub-directory of path specified by <include>")
@click.option('--yes', is_flag=True,
              help="skip double check")
@click.option('-s', '--suite-type', required=True, type=click.Choice(["testsuite", "benchmark"]), help="suite type")
@click.pass_context
def upload(ctx, include, exclude, glob, yes, suite_type):
    namespace = ctx.obj["namespace"]
    config_inst = ctx.obj["config"]

    echo.echo(f"testsuite namespace: {namespace}", fg='red')
    echo.echo("loading testsuites:")
    suffix = "benchmark.json" if suite_type == "benchmark" else "testsuite.json"
    suites = _load_testsuites(includes=include, excludes=exclude, glob=glob,
                              suffix=suffix, suite_type=suite_type)

    for suite in suites:
        echo.echo(f"\tdataset({len(suite.dataset)}) {suite.path}")
    if not yes and not click.confirm("running?"):
        return
    with Clients(config_inst) as client:
        for i, suite in enumerate(suites):
            # noinspection PyBroadException
            try:
                echo.echo(f"[{i + 1}/{len(suites)}]start at {time.strftime('%Y-%m-%d %X')} {suite.path}", fg='red')
                try:
                    _upload_data(client, suite, config_inst)
                except Exception as e:
                    raise RuntimeError(f"exception occur while uploading data for {suite.path}") from e
            except Exception:
                exception_id = uuid.uuid1()
                echo.echo(f"exception in {suite.path}, exception_id={exception_id}")
                LOGGER.exception(f"exception id: {exception_id}")
            finally:
                echo.stdout_newline()
    echo.farewell()
    echo.echo(f"testsuite namespace: {namespace}", fg='red')


@data_group.command("delete")
@click.option('-i', '--include', required=True, type=click.Path(exists=True), multiple=True, metavar="<include>",
              help="include *benchmark.json under these paths")
@click.option('-e', '--exclude', type=click.Path(exists=True), multiple=True,
              help="exclude *benchmark.json under these paths")
@click.option('-g', '--glob', type=str,
              help="glob string to filter sub-directory of path specified by <include>")
@click.option('-s', '--suite-type', required=True, type=click.Choice(["testsuite", "benchmark"]), help="suite type")
@click.pass_context
def delete(ctx, include, exclude, glob, yes, suite_type):
    namespace = ctx.obj["namespace"]
    config_inst = ctx.obj["config"]

    echo.echo(f"testsuite namespace: {namespace}", fg='red')
    echo.echo("loading testsuites:")
    suffix = "benchmark.json" if suite_type == "benchmark" else "testsuite.json"

    suites = _load_testsuites(includes=include, excludes=exclude, glob=glob,
                              suffix=suffix, suite_type=suite_type)
    if not yes and not click.confirm("running?"):
        return

    for suite in suites:
        echo.echo(f"\tdataset({len(suite.dataset)}) {suite.path}")
    if not yes and not click.confirm("running?"):
        return
    with Clients(config_inst) as client:
        for i, suite in enumerate(suites):
            _delete_data(client, suite)
    echo.farewell()
    echo.echo(f"testsuite namespace: {namespace}", fg='red')