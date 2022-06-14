#include "unrealircd.h"
 
// cleared up some weird duplication up here - Valware
 
#define SAQUITLOL "SAQUIT"
 
CMD_FUNC(saquit);
 
ModuleHeader MOD_HEADER =
{
	"third/saquit", 
	"0.1",
	"Provides SAQUIT command to force a user to quit lmao", // added the description which is needed for the module to load
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
	/* some declarations */
	Client *target; /* who we fuckin up today, boss */
	char p[150] = "\0";
	char reason[300] = "Quit: "; // Fake quit lol
	int i; // iter8or
 
    	/* ur penis I mean text is too sm0l */
	if (!parv[1] || BadPtr(parv[1]))
	{
		sendnumeric(client, ERR_NEEDMOREPARAMS, SAQUITLOL); // can't do it lmao
		return;
	}
	
	/* shove it all into your arse I mean into one parv */
	if (!BadPtr(parv[2]))
	{
		for (i = 2; i < parc && !BadPtr(parv[i]); i++)
		{
			strlcat(p, parv[i], sizeof(p)); // add it
			if (!BadPtr(parv[i + 1])) // check if there's one in front/ if we are looping again
				strlcat(p, " ", sizeof(p)); // if so, add a space so our words are still spaced out like me
		}
		const char *txt = p; // we put into txt const char
		strlcat(reason,txt,sizeof(reason)); // add our reason
	}
	
	
	
	if (!(target = find_user(parv[1],NULL))) // if we can't find the target
	{
		sendnumeric(client, ERR_NOSUCHNICK, parv[1]); // tell them about it and
		return; // ABORT
	}
	exit_client(target, recv_mtags, reason); /* bye bye fren */
}
