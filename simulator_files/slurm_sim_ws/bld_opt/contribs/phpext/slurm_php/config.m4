##*****************************************************************************
#  AUTHOR:
#    Danny Auble <da@llnl.gov>
#
#  DESCRIPTION:
#    Use to make the php slurm extension
##*****************************************************************************
PHP_ARG_WITH(slurm, whether to use slurm,
[ --with-slurm SLURM install dir])

AC_MSG_CHECKING([for phpize in default path])
if test ! -f "/usr/bin/phpize"; then
   PHP_SLURM="no"
   AC_MSG_RESULT([NO, CANNOT MAKE SLURM_PHP])
else
   AC_MSG_RESULT([yes])
fi

if test "$PHP_SLURM" != "no"; then
	SLURMLIB_PATH="/home/slurm/slurm_sim_ws/slurm_opt/lib ../../../src/db_api/.libs"
	SLURMINCLUDE_PATH="/home/slurm/slurm_sim_ws/slurm_opt/include"
	SEARCH_FOR="libslurmdb.so"

	# --with-libslurm -> check with-path

	if test -r $PHP_SLURM/; then # path given as parameter
		SLURM_DIR=$PHP_SLURM
		SLURMLIB_PATH="$SLURM_DIR/lib"
	else # search default path list
		AC_MSG_CHECKING([for libslurmdb.so in default paths])
		for i in $SLURMLIB_PATH ; do
			if test -r $i/$SEARCH_FOR; then
				SLURM_DIR=$i
				PHP_ADD_LIBPATH($i, SLURM_PHP_SHARED_LIBADD)

				AC_MSG_RESULT([found in $i])

			fi
		done
	fi

	if test -z "$SLURM_DIR"; then
		AC_MSG_RESULT([not found])
		AC_MSG_ERROR([Please reinstall the slurm distribution])
	fi

	PHP_ADD_INCLUDE($SLURMINCLUDE_PATH)
	PHP_ADD_INCLUDE(../../../../slurm_simulator)

	LIBNAME=slurmdb
	LIBSYMBOL=slurm_acct_storage_init

	PHP_CHECK_LIBRARY($LIBNAME, $LIBSYMBOL,
		[PHP_ADD_LIBRARY($LIBNAME, , SLURM_PHP_SHARED_LIBADD)
    			AC_DEFINE(HAVE_SLURMLIB,1,[ ])],
		[AC_MSG_ERROR([wrong libslurmdb version or lib not found])],
		[-L$SLURM_DIR -l$LIBNAME])


	PHP_SUBST(SLURM_PHP_SHARED_LIBADD)

	AC_CHECK_HEADERS(stdbool.h)

	AC_DEFINE(HAVE_SLURM_PHP, 1, [Whether you have SLURM])
	#PHP_EXTENSION(slurm_php, $ext_shared)
	PHP_NEW_EXTENSION(slurm_php, ../../../../slurm_simulator/contribs/phpext/slurm_php/slurm_php.c, $ext_shared)
fi
