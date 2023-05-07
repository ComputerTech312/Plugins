#include "unrealircd.h"
 
#define SAQUITLOL "SAQUIT"
 
CMD_FUNC(saquit);
 
ModuleHeader MOD_HEADER =
{
	"third/saquit", 
	"0.1",
	"Provides SAQUIT command to force a user to quit.",
	"ComputerTech",
	"unrealircd-6",
};
 
MOD_INIT() {
 
	MARK_AS_GLOBAL_MODULE(modinfo);
	CommandAdd(modinfo->handle, SAQUITLOL, saquit, 3, CMD_USER);
 
	return MOD_SUCCESS;
}
 
MOD_LOAD() {
	return MOD_SUCCESS;
}
 
MOD_UNLOAD() {
	return MOD_SUCCESS;
}
CMD_FUNC(saquit)
{
	
	Client *target; 
	char p[150] = "\0";
	char reason[300] = "Quit: ";
	int i;
 
    	
	if (!parv[1] || BadPtr(parv[1]))
	{
		sendnumeric(client, ERR_NEEDMOREPARAMS, SAQUITLOL);
		return;
	}
	

	if (!BadPtr(parv[2]))
	{
		for (i = 2; i < parc && !BadPtr(parv[i]); i++)
		{
			strlcat(p, parv[i], sizeof(p));
			if (!BadPtr(parv[i + 1])) 
				strlcat(p, " ", sizeof(p)); 
		}
		const char *txt = p; 
		strlcat(reason,txt,sizeof(reason)); 
	}
	
	
	
	if (!(target = find_user(parv[1],NULL)))
	{
		sendnumeric(client, ERR_NOSUCHNICK, parv[1]);
		return; // ABORT
	}
	exit_client(target, recv_mtags, reason);
}
