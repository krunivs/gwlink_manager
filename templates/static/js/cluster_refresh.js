// // request update cluster component
// function updateClusterComponentCondition(cluster) {
//     return $.ajax({
//         url: `/api/app/v1/clusters/${cluster}/conditions`,
//         type: "GET",
//         headers: {
//             Authorization: "Bearer " + Cookies.get("token")
//         },
//         success: function (response) {
//             let clusters = response['clusters'];
//             if (clusters === null || clusters === undefined || clusters.length <= 0) {
//                 return
//             }
//             if (clusters[0].hasOwnProperty('conditions') === false || clusters[0].conditions.length <= 0) {
//                 return
//             }
//             $('#cluster-conditions').empty();
//             $.each(clusters[0].conditions, (i, condition) => {
//                 let update_datetime = condition.updated.replace('T', ' ');
//                 update_datetime = update_datetime.replace('Z', ' ');
//
//                 $('#cluster-conditions').append(`
//                     <tr>
//                       <td width="5%"/>
//                       <td width="15%">
//                         ${condition.condition}
//                       </td>
//                       <td width="10%">
//                         ${condition.status}
//                       </td>
//                       <td width="10%">
//                         ${update_datetime}
//                       </td>
//                       <td width="40%" class="text-left" >
//                         &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;${condition.message}
//                       </td>
//                       <td width="20%"/>
//                     </tr>
//                 `);
//             });
//         },
//         error: function (error) {
//             console.log(error);
//         }
//     })
// }
//
// // update timer for cluster component conditions
// // timer interval: 3000
// window.setInterval(function () {
//
//     let clusterName = Cookies.get("selectedCluster");
//
//     updateClusterComponentCondition(clusterName);
// }, 3000);
